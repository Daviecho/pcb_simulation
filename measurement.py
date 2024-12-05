class Measurement:
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost):
        self.idMeasurement = idMeasurement
        self.name = nameMeasurement
        self.accuracy = accuracy
        self.duration = duration
        self.cost = cost

    def get_accuracy(self, defect_name):
        return self.accuracy.get(defect_name, 0)
