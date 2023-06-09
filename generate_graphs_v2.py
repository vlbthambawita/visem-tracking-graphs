import os
import numpy as np
import networkx as nx
from tqdm import tqdm


max_frame_number = 0 # This is used to keep track of the maximum frame number in the dataset

# Set the directory containing the text files
def generate_graphs(input_directory, output_directory, spatial_threshold):

    def euclidean_distance(center1, center2):
        return np.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

    def load_data_from_file(file_path, frame_number):
        data = []
        global max_frame_number # This is used to keep track of the maximum frame number in the dataset
        if frame_number > max_frame_number:
            max_frame_number = frame_number
        with open(file_path, 'r') as f:
            for line in f:
                # Assuming each line in the text file is in the format: sperm_id class x_center y_center width height
                sperm_id, class_name, x_center, y_center, width, height = line.strip().split()
                data.append((sperm_id, str(class_name), [float(x_center), float(y_center), float(width), float(height)], frame_number))
        return data

    # Set the directory containing the text files
    data_directory = input_directory

    # Load the dataset from the text files
    dataset = []
    for file_name in os.listdir(data_directory):
        frame_number = int(file_name.split('.')[0].split("_")[2])  # Assuming the frame number is the first part of the file name
        file_path = os.path.join(data_directory, file_name)
        
        dataset.extend(load_data_from_file(file_path, frame_number))

    # Create the graphs
    frame_graphs = [nx.Graph() for _ in range(max_frame_number + 1)]

    for sperm_id, class_name, yolo_coordinates, frame_number in dataset:
        #frame_graphs[frame_number].add_node(sperm_id, class_name=str(class_name), coordinates=list(yolo_coordinates))
        frame_graphs[frame_number].add_node(sperm_id, frame_number=frame_number, class_name=class_name, x_center=yolo_coordinates[0], y_center=yolo_coordinates[1], width=yolo_coordinates[2], height=yolo_coordinates[3])

    for frame_graph in frame_graphs:
        for sperm_id1, data1 in frame_graph.nodes(data=True):
            for sperm_id2, data2 in frame_graph.nodes(data=True):
                if sperm_id1 != sperm_id2:
                    #center1 = (data1['coordinates'][0], data1['coordinates'][1])
                    #center2 = (data2['coordinates'][0], data2['coordinates'][1])
                    center1 = (data1['x_center'], data1['y_center'])
                    center2 = (data2['x_center'], data2['y_center'])
                    distance = euclidean_distance(center1, center2)

                    if distance < spatial_threshold:
                        frame_graph.add_edge(sperm_id1, sperm_id2, weight=distance, edge_type="spatial")

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
                    video_graph.add_edge(sperm_id1, sperm_id2, edge_type="temporal")


    # Save the graphs to disk

    # Set the directory where you want to save the graphs
    frame_graph_output_directory = os.path.join(output_directory, 'frame_graphs')
    os.makedirs(frame_graph_output_directory, exist_ok=True)
    

    # Save the individual frame graphs
    for i, frame_graph in enumerate(frame_graphs):
        output_file_path = os.path.join(frame_graph_output_directory, f'frame_graph_{i}.graphml')
        nx.write_graphml(frame_graph, output_file_path)

    # Save the video graph
    output_file_path = os.path.join(output_directory, 'video_graph.graphml')
    nx.write_graphml(video_graph, output_file_path)




if __name__ == '__main__':

    input_root_dir = "/work/vajira/DATA/VISEM-Tracking-from_kaggle/VISEM_Tracking_Train_v4/Train"
    
    spatial_thresholds = [0.10, 0.20, 0.30, 0.40, 0.50] # This is the maximum distance between two nodes for them to be connected in the graph
    
    # Iterate through the spatial thresholds
    for spatial_threshold in tqdm(spatial_thresholds): 
        output_root_dir = "/work/vajira/DATA/visem-tracking-graphs" + "/spatial_threshold_" + str(spatial_threshold)
        os.makedirs(output_root_dir, exist_ok=True) 

        # Iterate through the files in the input directory
        for dir in tqdm(os.listdir(input_root_dir)):
            input_directory = os.path.join(input_root_dir, dir, "labels_ftid")
            output_directory = os.path.join(output_root_dir, dir)
            os.makedirs(output_directory, exist_ok=True)
            
            # Generate the graphs and save them to disk
            generate_graphs(input_directory, output_directory, spatial_threshold)
