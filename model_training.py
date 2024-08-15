import pickle
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

data_dict = json.load(open('./right_hand_data.json', 'rb'))

# Determine the maximum sequence length in your data
max_length = max(len(seq) for seq in data_dict['data'])

# Initialize an empty array to store the data
data = np.zeros((len(data_dict['data']), max_length))

# Fill the data array with your sequences
for i, seq in enumerate(data_dict['data']):
    data[i, :len(seq)] = seq

#data = np.asarray(data_dict['data'])
labels = np.asarray(data_dict['labels'])

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

model = RandomForestClassifier()

model.fit(x_train, y_train)

# Make predictions on the test set
y_predict = model.predict(x_test)

score = accuracy_score(y_predict, y_test)

print('{}% of samples were classified correctly !'.format(score * 100))

# Confusion Matrix
conf_mat = confusion_matrix(y_test, y_predict)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_mat, annot=True, fmt='d', cmap='Blues', xticklabels=np.unique(labels), yticklabels=np.unique(labels))
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# Classification Report
class_report = classification_report(y_test, y_predict)
print('Classification Report:\n', class_report)

# Bar Plot of Class Distribution
class_counts = np.bincount(labels)
plt.figure(figsize=(10, 6))
sns.barplot(x=np.unique(labels), y=class_counts[1:])
plt.xlabel('Class')
plt.ylabel('Count')
plt.title('Class Distribution')
plt.show()

#f = open('left_trained_model.p', 'wb')
#pickle.dump({'model': model}, f)
#f.close()