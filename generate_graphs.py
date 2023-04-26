import os
import numpy as np
import networkx as nx

def euclidean_distance(center1, center2):
    return np.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

def load_data_from_file(file_path, frame_number):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            # Assuming each line in the text file is in the format: sperm_id class x_center y_center width height
            sperm_id, class_name, x_center, y_center, width, height = line.strip().split()
            data.append((int(sperm_id), class_name, (float(x_center), float(y_center), float(width), float(height)), frame_number))
    return data

# Set the directory containing the text files
data_directory = "/work/vajira/DATA/VISEM-Tracking-from_kaggle/VISEM_Tracking_Train_v4/Train/11/labels_ftid"

# Load the dataset from the text files
dataset = []
for file_name in os.listdir(data_directory):
    frame_number = int(file_name.split('.')[0])  # Assuming the frame number is the first part of the file name
    file_path = os.path.join(data_directory, file_name)
    
    dataset.extend(load_data_from_file(file_path, frame_number))

# count the number of text files in the directory
def count_files(directory):
    return len([file for file in os.listdir(directory) if file.endswith('.txt')])

number_of_frames = count_files(data_directory)  # Set the total number of frames in your dataset

frame_graphs = [nx.Graph() for _ in range(number_of_frames)]

for sperm_id, class_name, yolo_coordinates, frame_number in dataset:
    frame_graphs[frame_number].add_node(sperm_id, class_name=class_name, coordinates=yolo_coordinates)

spatial_threshold = 0.25 # Set an appropriate threshold based on your data, this is based on the YOLO coordinates

for frame_graph in frame_graphs:
    for sperm_id1, data1 in frame_graph.nodes(data=True):
        for sperm_id2, data2 in frame_graph.nodes(data=True):
            if sperm_id1 != sperm_id2:
                center1 = (data1['coordinates'][0], data1['coordinates'][1])
                center2 = (data2['coordinates'][0], data2['coordinates'][1])
                distance = euclidean_distance(center1, center2)

                if distance < spatial_threshold:
                    frame_graph.add_edge(sperm_id1, sperm_id2, weight=distance)

video_graph = nx.DiGraph()

for frame_number, frame_graph in enumerate(frame_graphs):
    video_graph.add_nodes_from(frame_graph.nodes(data=True))
    video_graph.add_edges_from(frame_graph.edges(data=True))

for frame_number in range(len(frame_graphs) - 1):
    frame1_nodes = frame_graphs[frame_number].nodes()
    frame2_nodes = frame_graphs[frame_number + 1].nodes()

    for sperm_id1 in frame1_nodes:
        for sperm_id2 in frame2_nodes:
            if sperm_id1 == sperm_id2:  # Same sperm_id across consecutive frames
                video_graph.add_edge(sperm_id1, sperm_id2)


# Save the graphs to disk
import os

# Set the directory where you want to save the graphs
output_directory = "/work/vajira/DATA/visem-traking-graphs/11"

# Save the individual frame graphs
for i, frame_graph in enumerate(frame_graphs):
    output_file_path = os.path.join(output_directory, f'frame_graph_{i}.graphml')
    nx.write_graphml(frame_graph, output_file_path)

# Save the video graph
output_file_path = os.path.join(output_directory, 'video_graph.graphml')
nx.write_graphml(video_graph, output_file_path)
