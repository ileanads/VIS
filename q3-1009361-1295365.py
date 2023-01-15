from sklearn.base import BaseEstimator, ClassifierMixin
import numpy as np

class KNN(BaseEstimator, ClassifierMixin):

    def __init__(self, n_neighbors, metric, voting, embeddings):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.voting = voting
        self.embeddings = embeddings
        self.data = None

    def embed(self, X):
        if self.embeddings is None:
            return X
        X_embedded = []
        for doc in X:
            doc_embedding = np.zeros(self.embeddings.vector_size)
            for token in doc:
                doc_embedding += self.embeddings.get_vector(token)
            doc_embedding /= len(doc)
            X_embedded.append(doc_embedding)

        return X_embedded


    def distance(self, a, b):
        if self.metric == "cosine":
            cos = np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)))
            return 1 - cos
        elif self.metric == "euclidean":
            a = np.array(a)
            b = np.array(b)
            return np.linalg.norm(a - b)

    def vote(self, y, distances):
        if self.voting == "majority":
            return max(set(y), key=y.count)
        elif self.voting == "weighted":
            y_distances = {}
            for i in range(len(y)):
              v = y[i]
              distance = distances[i]
              if v not in y_distances:
                  y_distances[v] = distance
              else:
                  y_distances[v] += distance           
            return min(y_distances, key=y_distances.get)

    def fit(self, X, y):
        X_vectors = self.embed(X)
        dt = ()
        for x, i in zip(X_vectors, y):
          dt = (*dt, (x,i))
          self.data =dt
        return self

    def predict(self, x):
      if self.embeddings is not None:
        x = self.embed([x])[0]

      distances = []
      labels = []
      for vector, label in self.data:
        distances.append(self.distance(x, vector))
        labels.append(label)

      nearest_indices = np.argpartition(distances, self.n_neighbors)[:self.n_neighbors]

      nearest_labels = [labels[i] for i in nearest_indices]

      return self.vote(nearest_labels, distances)


    