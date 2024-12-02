class Measurement:
    def __init__(self, idMeasurement, nameMeasurement, accuracy, duration, cost):
        self.idMeasurement = idMeasurement  # Identificatore univoco del test
        self.nameMeasurement = nameMeasurement  # Nome del test
        self.accuracy = accuracy  # Dizionario con l'accuratezza per ciascun difetto
        self.duration = duration  # Durata del test
        self.cost = cost  # Costo del test

    def get_accuracy(self, defect_name):
        """
        Restituisce l'accuratezza del test per un certo difetto.
        """
        return self.accuracy.get(defect_name, 0)
