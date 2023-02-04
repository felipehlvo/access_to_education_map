import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from access import Access, weights, Datasets
import geopandas as gpd
from shapely import wkt
import access


# Average quality
def average_quality(
    loc_df,
    cost_df,
    max_cost=None,
    cost_source="origin",
    cost_dest="dest",
    cost_cost="cost",
    loc_index="geoid",
    loc_value=None,
    quality_value = None,
    weight_fn=None,
):
    """
    Calculation of the floating catchment (buffered) accessibility
    sum, from DataFrames with computed distances.
    This catchment may be either a simple buffer -- with cost below
    a single threshold -- or an additional weight may be applied
    as a function of the access cost.
    Parameters
    ----------
    loc_df         : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                 should contain at _least_ a list of the locations (`df_dest`) at which facilities are located.
    loc_index   : {bool, str}
                 is the the name of the df column that holds the facility locations.
                 If it is a bool, then the it the location is already on the index.
    loc_value   : str
                 If this value is `None`, a count will be used in place of a weight.
                 Use this, for instance, to count restaurants, instead of total doctors in a practice.
    cost_df    : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                 This dataframe contains the precomputed costs from an origin/index location to destinations.
    cost_source : str
                 The name of the column name of the index locations -- this is what will be grouped.
    cost_dest  : str
                 The name of the column name of the destination locations.
                 This is what will be _in_ each group.
    cost_cost  : str
                 This is is the name of the cost column.
    weight_fn  : function
                 This function will weight the value of resources/facilities,
                 as a function of the raw cost.
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                 note that it applies _along with_ the weight function.
    Returns
    -------
    resources  : pandas.Series
                 A -- potentially weighted -- sum of resources, facilities, or consumers.
    """
    # merge the loc dataframe and cost dataframe together
    if loc_index is True:
        temp = pd.merge(cost_df, loc_df, left_on=cost_source, right_index=True)
    else:
        temp = pd.merge(cost_df, loc_df, left_on=cost_source, right_on=loc_index)

    # constrain by max cost
    if max_cost is not None:
        temp = temp[temp[cost_cost] < max_cost].copy()

    # apply a weight function if inputted -- either enhanced two stage or three stage
    if weight_fn:
        new_loc_value_column = temp[loc_value] * temp.W3 * temp.G
        quality_column = temp[loc_value] * temp.W3 * temp.G * temp.C
        temp = temp.drop([loc_value], axis=1)
        temp[loc_value] = new_loc_value_column
        temp[quality_value] = quality_column

    access_sum = temp.groupby([cost_dest])[loc_value].sum()
    quality_sum = temp.groupby([cost_dest])[quality_value].sum()
    average_quality_series = quality_sum/access_sum
    
    return average_quality_series


from access.fca import weighted_catchment


def mod_three_stage_fca(
    demand_df,
    supply_df,
    cost_df,
    max_cost,
    demand_index="geoid",
    demand_name="demand",
    supply_index="geoid",
    supply_name="supply",
    cost_origin="origin",
    cost_dest="dest",
    cost_name="cost",
    # ADDED VALUE
    quality_name = "quality",
    weight_fn=None,
    normalize=False,
    
):
    """Calculation of the three-stage floating catchment accessibility
    ratio, from DataFrames with precomputed distances.
    This is accomplished through a single call of the :meth:`access.access.weighted_catchment` method,
    to retrieve the patients using each provider.
    The ratio of providers per patient is then calculated at each care destination,
    and that ratio is weighted and summed at each corresponding demand site.
    The only difference weight respect to the 2SFCA method is that,
    in addition to a distance-dependent weight (`weight_fn`),
    a preference weight *G* is calculated.  That calculation
    uses the value :math:`\\beta`.
    See the original paper by Wan, Zou, and Sternberg. :cite:`2012_wan_3SFCA`
    Parameters
    ----------
    demand_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and a total demand.
    demand_origin : str
                    is the name of the column of `demand` that holds the origin ID.
    demand_value  : str
                    is the name of the column of `demand` that holds the aggregate demand at a location.
    supply_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and level of supply
    supply_df     : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    The origins dataframe, containing a location index and level of supply
    cost_df       : `pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_
                    This dataframe contains a link between neighboring demand locations, and a cost between them.
    cost_origin   : str
                    The column name of the locations of users or consumers.
    cost_dest     : str
                    The column name of the supply or resource locations.
    cost_name     : str
                    The column name of the travel cost between origins and destinations
    weight_fn  : function
                 This fucntion will weight the value of resources/facilities,
                 as a function of the raw cost.
    max_cost   : float
                 This is the maximum cost to consider in the weighted sum;
                 note that it applies *along with* the weight function.
    preference_weight_beta : float
                             Parameter scaling with the gaussian weights,
                             used to generate preference weights.
    Returns
    -------
    access     : pandas.Series
                 A -- potentially-weighted -- three-stage access ratio.
    """

    from access import fca
    from access.fca import weighted_catchment
    
    # create preference weight 'G', which is the weight
    cost_df["W3"] = cost_df[cost_name].apply(weight_fn)
    cost_df["C"] = cost_df[quality_name]
    cost_df["W3C"] = cost_df["W3"] * cost_df["C"]
    W3Csum_frame = (
        cost_df[[cost_origin, "W3C"]]
        .groupby(cost_origin)
        .sum()
        .rename(columns={"W3C": "W3Csum"})
        .reset_index()
    )
    cost_df = pd.merge(cost_df, W3Csum_frame)
    cost_df["G"] = cost_df.W3C / cost_df.W3Csum
    
    # get a series of total demand then calculate the supply to total demand ratio for each location
    print("Calculating supply locations...")
    total_demand_series = weighted_catchment(
        demand_df,
        cost_df,
        max_cost,
        cost_source=cost_origin,
        cost_dest=cost_dest,
        cost_cost=cost_name,
        loc_index=demand_index,
        loc_value=demand_name,
        weight_fn=weight_fn,
        three_stage_weight=True,
    )

    # create a temporary dataframe, temp, that holds the supply and aggregate demand at each location
    total_demand_series.name += "_W"
    temp = supply_df.join(total_demand_series, how="right")

    # there may be NA values due to a shorter supply dataframe than the demand dataframe.
    # in this case, replace any potential NA values(which correspond to supply locations with no supply) with 0.
    temp[supply_name].fillna(0, inplace=True)

    # calculate the fractional ratio of supply to aggregate demand at each location, or Rl
    temp["Rl"] = temp[supply_name] / temp[demand_name + "_W"]

    # separate the fractional ratio of supply to aggregate demand at each location, or Rl, into a new dataframe
    supply_to_total_demand_frame = pd.DataFrame(data={"Rl": temp["Rl"]})
    supply_to_total_demand_frame.index.name = "geoid"

    print("Calculating demand locations...")
    # sum, into a series, the supply to total demand ratios for each location
    three_stage_fca_series = weighted_catchment(
        supply_to_total_demand_frame,
        cost_df.sort_index(),
        max_cost,
        cost_source=cost_dest,
        cost_dest=cost_origin,
        cost_cost=cost_name,
        loc_index="geoid",
        loc_value="Rl",
        weight_fn=weight_fn,
        three_stage_weight=True,
    )

    print("Calculating average quality...")
    average_quality_series = average_quality(
        supply_to_total_demand_frame,
        cost_df.sort_index(),
        max_cost,
        cost_source=cost_dest,
        cost_dest=cost_origin,
        cost_cost=cost_name,
        loc_index="geoid",
        loc_value="Rl",
        weight_fn=weight_fn
    )

    # remove the preference weight G from the original costs dataframe
    cost_df.drop(columns=["G", "W3", "W3Csum"], inplace=True)

    return three_stage_fca_series, average_quality_series


def class_mod_three_stage_fca(
    self,
    name="3sfca",
    quality_name = "Q",
    quality = "quality",
    cost=None,
    supply_values=None,
    max_cost=None,
    weight_fn=None,
    normalize=False
):
    """Calculate the three-stage floating catchment area access score.
    Parameters
    ----------
    name                : str
                            Column name for access values
    cost                : str
                            Name of cost value column in cost_df (supply-side)
    max_cost            : float
                            Cutoff of cost values
    weight_fn           : function
                            Weight to be applied to access values
    normalize           : bool
                            If True, return normalized access values; otherwise, return raw access values
    Returns
    -------
    access              : pandas Series
                            Accessibility score for origin locations.
    """
    from access import helpers
    assert (
        self.supply_value_provided == True
    ), "You must provide a supply value in order to use this functionality."

    if weight_fn is None:
        weight_fn = weights.step_fn({10: 0.962, 20: 0.704, 30: 0.377, 60: 0.042})

    cost = helpers.sanitize_supply_cost(self, cost, name)
    supply_values = helpers.sanitize_supplies(self, supply_values)

    for s in supply_values:

        series, avg_quality = mod_three_stage_fca(
            demand_df=self.demand_df,
            demand_index=self.demand_df.index.name,
            demand_name=self.demand_value,
            supply_df=self.supply_df,
            supply_index=self.supply_df.index.name,
            supply_name=s,
            cost_df=self.cost_df,
            cost_origin=self.cost_origin,
            cost_dest=self.cost_dest,
            cost_name=cost,
            max_cost=max_cost,
            weight_fn=weight_fn,
            normalize=normalize,
            quality_name=quality
            
        )

        series.name = name + "_" + s
        avg_quality.name = quality_name + "_" + s
        if series.name in self.access_df.columns:
            self.log.info("Overwriting {}.".format(series.name))
            self.access_df.drop(series.name, axis=1, inplace=True)

        # store the raw, un-normalized access values
        self.access_df = self.access_df.join(series)
        self.access_df = self.access_df.join(avg_quality)

        self.avg_quality = avg_quality
        self.access = series

    if normalize:

        columns = [name + "_" + s for s in supply_values]
        return helpers.normalized_access(self, columns)

    return self.access_df.filter(regex="^" + name, axis=1)