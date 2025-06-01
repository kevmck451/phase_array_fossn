



class Anomaly_Filter:

    def __init__(self):
        self.bias_scale_factor = 0.99
        self.bias_margin = 0.5
        self.bias_theta_ratio = 0.7
        self.edge_width = 4
        self.suppression_factor = 0.5
        self.targeted = False

    def remove_bias(self, anomalies):
        mean_val = sum(anomalies) / len(anomalies)
        if mean_val == 0:
            return anomalies  # avoid division by zero

        threshold = self.bias_margin * abs(mean_val)

        count_within_margin = sum(abs(a - mean_val) <= threshold for a in anomalies)
        ratio_within = count_within_margin / len(anomalies)

        if ratio_within >= self.bias_theta_ratio:
            bias = mean_val * self.bias_scale_factor

            # subtract only values in the margin
            if self.targeted:
                anomalies = [
                    max(0, int(round(a - bias))) if abs(a - mean_val) <= threshold else a
                    for a in anomalies]

            # subtract the mean from everything
            else: anomalies = [max(0, int(round(a - bias))) for a in anomalies]

        return anomalies

    def suppress_edges(self, anomalies):
        length = len(anomalies)
        new_anomalies = anomalies[:]

        for i in range(self.edge_width):
            scale = self.suppression_factor + (1 - self.suppression_factor) * (i / (self.edge_width - 1))
            new_anomalies[i] = int(round(new_anomalies[i] * scale))
            new_anomalies[length - 1 - i] = int(round(new_anomalies[length - 1 - i] * scale))

        return new_anomalies

    def process(self, anomalies):
        anomalies = self.remove_bias(anomalies)
        anomalies = self.suppress_edges(anomalies)

        return anomalies