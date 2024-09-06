
import numpy as np
from sklearn.covariance import MinCovDet
from scipy.spatial.distance import mahalanobis

# Sample multivariate data (e.g., 2D data points)
X = np.array([[2, 3], [3, 6], [5, 8], [8, 10], [7, 2], [10, 12], [11, 13]])

# Robustly estimate the covariance matrix and the mean using MCD
mcd = MinCovDet().fit(X)
robust_mean = mcd.location_  # Robust mean (mu_MCD)
robust_cov = mcd.covariance_  # Robust covariance matrix (Sigma_MCD)

# Invert the covariance matrix for the Mahalanobis distance formula
inv_cov_matrix = np.linalg.inv(robust_cov)

# Function to calculate Mahalanobis distance
def robust_mahalanobis_distance(x, mean, inv_cov):
    delta = x - mean
    return np.sqrt(np.dot(np.dot(delta, inv_cov), delta.T))

# Compute the Mahalanobis distance for each point in the dataset
distances = np.array([robust_mahalanobis_distance(x, robust_mean, inv_cov_matrix) for x in X])

print("Mahalanobis distances using MCD:", distances)

