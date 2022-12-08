# Mapa do Ensino Médio 📚
An interactive map measuring spatial access to public high schools in Brazil.

## Demo App

[Mapa do Ensino Médio](https://felipehlvo-access-to-education-map-app-b097xc.streamlit.app)

## Repository Structure

**Main Directory**

| File | Content |
| ------------- | ------------- |
| app.py | Contains the actual Streamlit application |
| requirements.txt | Contains all requirements (necessary for Streamlit sharing) |

**data/Final/**

| File | Content |
| ------------- | ------------- |
|schools_census.zip| data on the school census |
|dem_census_XXX.zip | data on the Demographic Census (split for because they are too large) |

**notebooks**
| File | Content |
| ------------- | ------------- |
| Data Importing.ipynb | Notebook used to download the data form Base Dos Dados |
| Create Dataset.ipynb | Notebook used to join census files |
| Building Basic Dataset.ipynb | Notebook used to extract data of interest from Census and School Census and make school.csv and census.csv |
| Creating the Distance Matrix.ipynb | Notebook for calculating the distance matrix between schools and census tracts |
| Access Metric - Brazil.ipynb | Jupyter Notebook calculating the accessibility metric |


## ⚙️ How to run the application locally?

```
# clone the repository
git clone https://github.com/felipehlvo/access_to_education_map.git

# Go to the directory of the repository
cd access_to_education_map

# Install required packages
pip install -r requirements.txt

# Run app
streamlit run app.py
```
