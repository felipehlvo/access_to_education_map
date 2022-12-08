def gaussian(sigma):
    import numpy as np

    return lambda x: np.exp(-x * x / (2 * sigma**2))

import matplotlib.pyplot as plt
import numpy as np
for i in range(10000, 1, -1):
    if gaussian(i)(16000) <= 0.01:
        print(i)
        x = np.linspace(0, 16000, 100)
        y = gaussian(i)(x)

        plt.plot(x, y)
        plt.show()
        break

x = np.linspace(0, 16000, 100)
y = gaussian(5000)(x)

plt.plot(x, y, color = "k")
plt.xlabel("Distance (meters)")
plt.ylabel("Weight")
plt.show()
print(gaussian(5000)(4000))
print(gaussian(5000)(8000))
print(gaussian(5000)(16000))