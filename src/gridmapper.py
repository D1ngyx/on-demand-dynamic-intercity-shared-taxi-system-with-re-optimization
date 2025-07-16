import numpy as np
import tqdm
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box, Point
from typing import Hashable, Union
from router import tt as tao

def remove_repeat_in_list(original_list):
    unique_list = []
    for item in original_list:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list


class GridMapper:
    def __init__(self, min_lon:float, min_lat:float, max_lon:float, max_lat:float, grid_size:float) -> None:
        lon_values = np.arange(min_lon, max_lon, grid_size)
        lat_values = np.arange(min_lat, max_lat, grid_size)
        lon_grid, lat_grid = np.meshgrid(lon_values, lat_values)
        self.grid_points = gpd.GeoDataFrame(geometry=[box(lon, lat, lon + grid_size, lat + grid_size) for lon, lat in zip(lon_grid.flatten(), lat_grid.flatten())])
        self.estimate_duration_matrix_np = np.full((len(self.grid_points), len(self.grid_points)), -1)

    def generate_random_coordinates(self, num_points: int, decimal_places: int = 6) -> list[list[tuple[float,float]]]:
        random_coords_in_grid = []
        np.random.seed(42)  
        for idx, row in self.grid_points.iterrows():
            lon_values = np.random.uniform(row.geometry.bounds[0], row.geometry.bounds[2], num_points)
            lat_values = np.random.uniform(row.geometry.bounds[1], row.geometry.bounds[3], num_points)
            coordinates = [(round(lon, decimal_places), round(lat, decimal_places)) for lon, lat in zip(lon_values, lat_values)]
            random_coords_in_grid.append(coordinates)
        return random_coords_in_grid

    def get_grid_id_by_coordinate(self, lon: Union[str, float], lat: Union[str, float]) -> Hashable:
        lon = float(lon)
        lat = float(lat)
        point = Point(lon, lat) 
        for idx, row in self.grid_points.iterrows():
            if point.within(row.geometry):
                return idx
        return -1

    def offline_generate_estimate_duration_between_grid(self, random_in_grid:list[list[tuple]]):
        n = len(random_in_grid)
        for i in tqdm.trange(n):      # i-th 
            for j in range(n):        # j-th 
                if i==j:
                    continue
                tempo = []
                for coord_from_i in random_in_grid[i]:
                    for coord_from_j in random_in_grid[j]:
                        tempo.append(tao([coord_from_i,coord_from_j]))
                self.estimate_duration_matrix_np[i,j] = sum(tempo)/len(tempo)

    def visualize_map(self, highlighted_regions: list[int], connection_order: list[int]) -> None:
        highlighted_regions = remove_repeat_in_list(highlighted_regions)
        connection_order = remove_repeat_in_list(connection_order)      
        fig, ax = plt.subplots(figsize=(10, 8))

        self.grid_points.plot(ax=ax, color='none', edgecolor='red', linewidth=1)

        for idx, row in self.grid_points.iterrows():
            plt.text(row.geometry.centroid.x, row.geometry.centroid.y, str(idx), fontsize=8, ha='center')

        if highlighted_regions:
            highlighted = self.grid_points.loc[highlighted_regions]
            highlighted.plot(ax=ax, color='green', alpha=0.5)  

        if connection_order:
            for i in range(len(connection_order) - 1):
                start_point = self.grid_points.loc[connection_order[i]].geometry.centroid
                end_point = self.grid_points.loc[connection_order[i + 1]].geometry.centroid
                plt.arrow(start_point.x, start_point.y, end_point.x - start_point.x, end_point.y - start_point.y,
                          head_width=0.05, head_length=0.05, fc='yellow', ec='blue')

        plt.title('Grid Visualization')
        plt.show()
    
""" Unit Test """
# GM = GridMapper(117.595, 24.4124, 118.343, 24.7566, 0.02)  
# GM = GridMapper(117.8158, 24.396, 118.3540, 25.271, 0.05)  
# GM.visualize_map([],[])
# res1 = GM.get_grid_id_by_coordinate(118.0, 24.5)
# res2 = GM.get_grid_id_by_coordinate(200.0, 24.5)
# print(res1, res2)
# print(type(res1), type(res2))
# grid_mapper = GridMapper(min_lon=0, min_lat=0, max_lon=2, max_lat=2, grid_size=1)

# random_coords_in_grid = GM.generate_random_coordinates(10)
# GM.offline_generate_estimate_duration_between_grid(random_coords_in_grid)
# np.save("estimate_duration_matrix_zhangzhou.npy", GM.estimate_duration_matrix_np)


