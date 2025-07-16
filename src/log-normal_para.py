" Used to fit the LOG-NORMAL distribution's mu and sigma parameters "

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm

# original data
# data = np.array([0.433, 0.128, 0.1, 0.079, 0.612, 0.448, 0.452])
# data = np.array([1.274, 0.37, 0.328, 0.35, 0.658, 0.675, 0.561])
# data = np.array([0.251, 0.241, 0.192, 0.092, 0.08, 0.29, 0.239 ])
# data = np.array([0.795, 0.409, 0.421, 0.527, 0.3, 0.338, 0.356])
# data = np.array([0.187, 0.207, 0.124, 0.107, 0.108, 0.318, 0.165])
# data = np.array([0.27, 0.848, 0.218, 0.238, 0.625, 0.256, 0.22])
data = np.array([0.08, 0.07, 0.1, 0.08, 0.07, 0.11, 0.06])

# log-normal，loc=0
shape, loc, scale = lognorm.fit(data, floc=0)
mu = np.log(scale)
sigma = shape

# generate PDF
x = np.linspace(min(data)*0.9, max(data)*1.1, 500)
pdf_fitted = lognorm.pdf(x, shape, loc, scale)

# visulize
plt.figure(figsize=(8, 5))
plt.hist(data, bins=6, density=True, alpha=0.5, label="Data Histogram")
plt.plot(x, pdf_fitted, 'r-', lw=2, label="Fitted Log-normal Distribution")
plt.title("Log-normal Fit of Congestion Coefficient")
plt.xlabel("Congestion Coefficient")
plt.ylabel("Probability Density")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

print(f"μ (mu) = {mu:.4f}")
print(f"σ (sigma) = {sigma:.4f}")


