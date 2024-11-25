class Measurement:
    def __init__(self, idMeasurement, nameMeasurement):
        self.idMeasurement = idMeasurement
        self.nameMeasurement = nameMeasurement
        self.accuracies = {}
        self.cost = 0

    def set_accuracy(self, defect_name, accuracy):
        """Sets the accuracy of this test for a specific defect."""
        if 0 <= accuracy <= 1:
            self.accuracies[defect_name] = accuracy
        else:
            raise ValueError("Accuracy must be between 0 and 1.")

    def get_accuracy(self, defect_name):
        """Returns the accuracy of the test for a specific defect."""
        return self.accuracies.get(defect_name, 0)
