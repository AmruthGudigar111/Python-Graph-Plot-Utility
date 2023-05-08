import tkinter as tk
from tkinter import filedialog
import networkx as nx
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os
import shutil
import tempfile


def load_config():
    file_path = filedialog.askopenfilename(title="Select Config File", filetypes=[("Config Files", "*.netsim")])
    if file_path:
        # Create a dictionary of node positions
        positions_dict = {}
        # Create a custom temporary directory
        temp_dir = tempfile.mkdtemp(prefix="Graph")

        # Copy files to the temporary directory
        src_path = file_path
        dst_path = os.path.join(temp_dir, "Configuration.xml")
        shutil.copy(src_path, dst_path)

        # Parse the XML file
        tree = ET.parse(dst_path)
        root = tree.getroot()

        # Create a new networkx graph
        g = nx.DiGraph()

        # set the plot window title
        plt.figure('Graph Plot')
        plt.title("Graph Plot", fontweight='bold')

        for device in root.findall('.//DEVICE'):
            device_name = device.get('DEVICE_NAME')
            pos_3d = device.find('POS_3D')
            if pos_3d is not None:
                x_or_lon = pos_3d.get('X_OR_LON')
                y_or_lat = pos_3d.get('Y_OR_LAT')
                positions_dict[device_name] = (x_or_lon, y_or_lat)

        # Add nodes to the graph with position information
        for device_name, pos in positions_dict.items():
            g.add_node(device_name, pos=pos)

        # create an empty list to store edges
        edges = []

        # loop through each LINK element in the XML
        for link in root.findall(".//LINK"):
            # get the medium type for the link
            medium = link.get('MEDIUM')
            # check if the medium type is wired or wireless
            if medium == 'WIRED':
                # if wired, add two edges (one for each device)
                device1 = link.findall("./DEVICE")[0]
                device2 = link.findall("./DEVICE")[1]
                # G.add_edge(device1.get("NAME"), device2.get("NAME"))
                edges.append((device1.get('NAME'), device2.get('NAME')))
            elif medium == 'WIRELESS':
                # if wireless, add edges between the access point and each device
                ap = link.findall("./DEVICE")[0]
                devices = link.findall("./DEVICE")
                for device in devices:
                    if device.get("NAME") != ap.get("NAME"):
                        edges.append((ap.get('NAME'), device.get('NAME')))
            else:
                # ignore other types of medium
                pass

        # Add edges to the graph
        g.add_edges_from(edges)

        # Draw the graph
        pos = nx.get_node_attributes(g, 'pos')
        pos = {k: tuple(map(float, v)) for k, v in pos.items()}

        nx.draw(g, pos=pos, with_labels=True, node_color='red', font_size=10, node_size=10, font_weight='bold')

        # adjust the subplot spacing
        plt.subplots_adjust(left=0, bottom=0, right=0.95, top=0.95, wspace=0.2, hspace=0.2)

        # To Destroy the old window
        window.destroy()

        # Delete the temporary directory
        shutil.rmtree(temp_dir)

        # Show the plot
        plt.show()


# Create a GUI window
window = tk.Tk()
window.title("Graph Plot")
window.geometry("250x70")  # Set the size to 400 pixels wide and 300 pixels tall

# Disable resizing of the main window
window.resizable(False, False)

# Add a button to load the configuration file
load_button = tk.Button(window, text="Load Configuration File", command=load_config)
load_button.place(x=55, y=20)

# Run the GUI window
window.mainloop()
