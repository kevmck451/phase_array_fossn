import numpy as np
from sklearn.decomposition import PCA
from sklearn.covariance import MinCovDet
from scipy.spatial.distance import mahalanobis
from queue import Queue


class AnomalyDetector:
    def __init__(self, num_components=3):
        self.num_components = num_components  # Number of principal components to use
        self.baseline_pca = None  # PCA for baseline
        self.baseline_mean = None  # Robust mean of baseline
        self.baseline_cov_inv = None  # Inverted covariance matrix for baseline
        self.baseline_distances = None  # Mahalanobis distances of the baseline
        self.queue = Queue()  # Queue to store the number of anomalies per channel

    def update_baseline(self, data):
        """ Update baseline using new data, apply PCA, and calculate robust statistics. """
        # Apply PCA to reduce dimensionality
        pca = PCA(n_components=self.num_components)
        principal_components = pca.fit_transform(data)

        # Robustly estimate the mean and covariance matrix
        mcd = MinCovDet().fit(principal_components)
        self.baseline_mean = mcd.location_
        robust_cov = mcd.covariance_
        self.baseline_cov_inv = np.linalg.inv(robust_cov)

        # Calculate Mahalanobis distances for the baseline data
        self.baseline_distances = np.array([self._mahalanobis_distance(x) for x in principal_components])
        self.baseline_pca = pca

    def _mahalanobis_distance(self, x):
        """ Calculate Mahalanobis distance for a point x using baseline mean and covariance. """
        delta = x - self.baseline_mean
        return np.sqrt(np.dot(np.dot(delta, self.baseline_cov_inv), delta.T))

    def detect_anomalies(self, new_data):
        """ Detect anomalies in new data based on the Mahalanobis distance from the baseline. """
        if self.baseline_pca is None:
            raise ValueError("Baseline is not set. Please call update_baseline first.")

        # Apply PCA using the baseline PCA transformation
        new_principal_components = self.baseline_pca.transform(new_data)

        # Calculate Mahalanobis distance for new data
        new_distances = np.array([self._mahalanobis_distance(x) for x in new_principal_components])

        # Calculate anomalies where the Mahalanobis distance exceeds a threshold
        anomaly_threshold = np.mean(self.baseline_distances) + 2 * np.std(self.baseline_distances)  # Example threshold
        anomalies = (new_distances > anomaly_threshold).astype(int)

        # Put the number of anomalies for each channel into the queue
        self.queue.put(np.sum(anomalies))

    def get_anomaly_count(self):
        """ Get the number of anomalies from the queue. """
        if not self.queue.empty():
            return self.queue.get()
        return 0


# Example Usage
detector = AnomalyDetector(num_components=3)

# Simulating baseline data collection
baseline_data = np.random.randn(100, 10)  # 100 samples, 10 features
detector.update_baseline(baseline_data)

# New data coming in for anomaly detection
new_data = np.random.randn(10, 10)  # 10 new samples, 10 features
detector.detect_anomalies(new_data)

# Get the number of anomalies detected
anomalies_count = detector.get_anomaly_count()
print("Number of anomalies detected:", anomalies_count)
