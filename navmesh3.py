import tkinter as tk
from tkinter import filedialog
import os
import json
import geojson
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from random import randint
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

# Definicja programu Navmesh
class NavmeshApp:
    def __init__(self): # Okno tkinter
        self.root = tk.Tk()
        self.root.title('Kreator Navmesh')
        self.root.state("zoomed")

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        # Widok mapy
        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        # Połączenia interkacji użytkownika
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect('motion_notify_event', self.update_coordinates)
        self.canvas.mpl_connect('scroll_event', self.zoom)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_press_event', self.start_pan)
        self.canvas.mpl_connect('motion_notify_event', self.pan)
        self.canvas.mpl_connect('button_release_event', self.end_pan)
        # Infoboxy
        self.status_bar = tk.Label(self.root, text='Współrzędne: N/A')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.help_lr = tk.Label(self.root, text='Warstwa pomocnicza: N/A')
        self.help_lr.pack(side=tk.BOTTOM, fill=tk.X)
        self.point_lr = tk.Label(self.root, text='Warstwa punktów: N/A')
        self.point_lr.pack(side=tk.BOTTOM, fill=tk.X)
        self.info = tk.Label(self.root, text='Instrukcja korzystania:\n\n1. Załaduj pliki warstw\n2. Wybierz promień połączeń\n3. Kliknij przycisk auto łączenia\n4. Użyj przycisku detekcji intersekcji\n5. Ręcznie popraw połączenia\n6. Zapisz wyniki\n\nAby edytować poprzedni projekt\nzaimportuj warstwę punktów\noraz warstwę nawigacji.\n\nSterowanie:\n\nPrzesuwanie - kliknij i przytrzymaj\nZoomowanie - scroll myszy\nPołącz punkty - PPM + tryb łączenia\nUsuń połączenie - PPM + tryb usuwania\n')
        self.info.pack(side=tk.BOTTOM, fill=tk.X)
        # Zmienne wejściowe
        self.points_data = None
        self.help_layer = None
        self.loaded_points = False
        self.lines_layer = gpd.GeoDataFrame(columns=['geometry', 'od', 'do'], crs='EPSG:4326')
        self.search_radius = 4 * 0.000009
        self.intersection_radius = 0.5 * 0.000009 # tymczasowy przelicznik CRS84 -> * 0.000009
        # Pasek opcji i przyciski
        self.control_frame = tk.Frame(self.root, width=300)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.control_frame, text="Dane wejściowe:").pack(fill=tk.X)
        tk.Button(self.control_frame, text='Warstwa punktowa', command=self.load_points_layer).pack(fill=tk.X)
        tk.Button(self.control_frame, text='Warstwa pomocnicza', command=self.load_help_layer).pack(fill=tk.X)

        tk.Label(self.control_frame, text="Narzędzia:").pack(fill=tk.X,pady=(10,0))
        self.connect_button = tk.Button(self.control_frame, text='Ręczne wybieranie połączeń',
                                        command=self.toggle_manual_connect)
        self.connect_button.pack(fill=tk.X)
        self.delete_button = tk.Button(self.control_frame, text='Ręczne usuwanie połączeń',
                                       command=self.toggle_manual_delete)
        self.delete_button.pack(fill=tk.X)
        tk.Label(self.control_frame, text='Promień łączenia:').pack()
        self.radius_input = tk.Entry(self.control_frame)
        self.radius_input.insert(0, str(self.search_radius))
        self.radius_input.pack()
        tk.Button(self.control_frame, text='Auto utwórz połączenia', command=self.create_lines_layer).pack(fill=tk.X)
        tk.Label(self.control_frame, text="Zapis/eksport:").pack(fill=tk.X, pady=(10, 0))
        tk.Button(self.control_frame, text='Zapisz jako...', command=self.save_layers).pack(fill=tk.X)
        tk.Button(self.control_frame, text='Eksportuj do JSON', command=self.export_to_json).pack(fill=tk.X)
        tk.Button(self.control_frame, text='Eksportuj do JavaScript', command=self.export_to_js).pack(fill=tk.X)

        tk.Label(self.control_frame, text="Edycja:").pack(fill=tk.X, pady=(10, 0))
        tk.Button(self.control_frame, text='Import warstwy nawigacji', command=self.load_nav_layer).pack(fill=tk.X)
        tk.Label(self.control_frame, text='Promień intersekcji:').pack()
        self.intersection_input = tk.Entry(self.control_frame)
        self.intersection_input.insert(0, str(self.intersection_radius))
        self.intersection_input.pack()
        tk.Button(self.control_frame, text='Sprawdź przecięcia linii', command=self.check_intersections).pack(fill=tk.X)
        tk.Label(self.control_frame, text="Inne:").pack(fill=tk.X, pady=(10, 0))
        self.dark_mode_button = tk.Button(self.control_frame, text='Tryb ciemny',
                                          command=self.toggle_dark_mode)
        self.dark_mode_button.pack(fill=tk.X)

        # Debounce dla przycisków
        self.manual_connect_mode = False
        self.manual_delete_mode = False
        self.selected_points = []
        self.pan_active = False
        self.pan_start = None
        self.dark_mode = False

    def toggle_dark_mode(self): # Tryb ciemny interfejsu
        self.dark_mode = not self.dark_mode
        bg_color = '#2E2E2E' if self.dark_mode else '#F0F0F0'
        fg_color = '#FFFFFF' if self.dark_mode else '#000000'

        self.root.configure(bg=bg_color)
        self.control_frame.configure(bg=bg_color)
        self.canvas_frame.configure(bg=bg_color)

        self.ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        self.ax.tick_params(colors=fg_color)
        self.ax.spines['top'].set_color(fg_color)
        self.ax.spines['bottom'].set_color(fg_color)
        self.ax.spines['left'].set_color(fg_color)
        self.ax.spines['right'].set_color(fg_color)
        self.ax.title.set_color(fg_color)
        self.ax.xaxis.label.set_color(fg_color)
        self.ax.yaxis.label.set_color(fg_color)

        self.status_bar.config(bg=bg_color, fg=fg_color)
        self.help_lr.config(bg=bg_color, fg=fg_color)
        self.point_lr.config(bg=bg_color, fg=fg_color)
        self.info.config(bg=bg_color, fg=fg_color)

        for widget in self.control_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg=bg_color, fg=fg_color, activebackground='#5E5E5E' if self.dark_mode else '#D9D9D9')
        #self.dark_mode_button.config(text='Tryb jasny' if self.dark_mode else 'Tryb ciemny')

    def load_points_layer(self):  # Funkcja otwierająca plik warstwy punktowej
        file_name = filedialog.askopenfilename(title='Otwórz plik wartwy punktów', filetypes=[('GeoPackage Files', '*.gpkg'),('GeoJSON Files', '*.json *.geojson *.js')])
        if file_name:
            if file_name.endswith(('.json', '.geojson', '.js')): # Dla edycji plików .json/js
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if file_name.endswith('.js'): # Usunięcie przedrostka z .js
                        content = re.sub(r'^var json_\w+\s*=\s*', '', content)
                    data = json.loads(content)
                    for feature in data['features']:
                        if 'Nav' in feature['properties']: # Konwersja atrybutu Nav na String
                            feature['properties']['Nav'] = str(feature['properties']['Nav'])
                self.points_data = gpd.GeoDataFrame.from_features(data['features'])
                self.points_data.set_crs(epsg=4326, inplace=True) # do zmiany na epsg 2180
            else:
                self.points_data = gpd.read_file(file_name)
            if 'fid' in self.points_data.columns:
                self.points_data = self.points_data.drop(columns=['fid'])
            #self.points_data = self.points_data.to_crs(epsg=2180)
            self.update_viewer()
            self.loaded_points = True
            short_name = os.path.basename(file_name)
            self.point_lr.config(text=f'Warstwa punktów: {short_name}')

    def load_help_layer(self): # Funkcja ładująca plik warstwy pomocniczej
        file_name = filedialog.askopenfilename(title='Otwórz plik warstwy pomocniczej', filetypes=[('GeoPackage Files', '*.gpkg'),('GeoJSON Files', '*.json *.geojson')])
        if file_name:
            self.help_layer = gpd.read_file(file_name)
            #self.help_layer = self.help_layer.to_crs(epsg=2180)
            self.update_viewer()
            short_name = os.path.basename(file_name)
            self.help_lr.config(text=f'Warstwa pomocnicza: {short_name}')

    def load_nav_layer(self): # Funkcja ładująca warstwę linii nawigacji do poprawek
        file_name = filedialog.askopenfilename(title='Otwórz plik GeoJSON', filetypes=[('GeoPackage Files', '*.gpkg'),('GeoJSON Files', '*.json *.geojson *.js')])
        if file_name:
            if file_name.endswith(('.json', '.geojson', '.js')):
                with open(file_name, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if file_name.endswith('.js'):
                        content = re.sub(r'^var json_\w+\s*=\s*', '', content)
                    data = json.loads(content)
                self.nav_layer = gpd.GeoDataFrame.from_features(data['features'])
                self.nav_layer.set_crs(epsg=4326, inplace=True) # do zmiany na 2180
                self.lines_layer = self.nav_layer
            else:
                self.nav_layer = gpd.read_file(file_name)
                self.lines_layer = self.nav_layer
                # self.nav_layer = self.nav_layer.to_crs(epsg=2180)
            self.nazwa_navfile = os.path.basename(file_name)
            if 'fid' in self.lines_layer.columns:
                self.lines_layer = self.lines_layer.drop(columns=['fid'])
            self.update_viewer()

    def update_viewer(self): # Odśwież widok
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        self.ax.cla()
        if self.help_layer is not None:
            self.help_layer.plot(ax=self.ax, color='green')
        if not self.lines_layer.empty:
            self.lines_layer.plot(ax=self.ax, color='blue')
        if self.points_data is not None:
            self.points_data.plot(ax=self.ax, color='red')
        if self.loaded_points==True:
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        self.canvas.draw()

    def create_lines_layer(self): # Automatyczne tworzenie połączeń według promienia szukania
        if self.points_data is not None:
            self.search_radius = float(self.radius_input.get())
            lines = []
            for idx, point in self.points_data.iterrows():
                neighbors = self.points_data[self.points_data.geometry.distance(point.geometry) < self.search_radius]
                neighbors = neighbors[neighbors.index != idx]
                # Zapisanie połączeń do tabeli atrybutów
                if 'Nav' not in self.points_data.columns:
                    self.points_data['Nav'] = ['[]'] * len(self.points_data)

                nav_list = eval(self.points_data.at[idx, 'Nav'])

                for n_idx, neighbor in neighbors.iterrows(): # Sprawdzenie duplikatów
                    if n_idx not in nav_list and idx not in eval(self.points_data.at[n_idx, 'Nav']):
                        line = LineString([point.geometry, neighbor.geometry])
                        lines.append({'geometry': line, 'od': idx, 'do': n_idx})

                        nav_list.append(n_idx)
                        self.points_data.at[idx, 'Nav'] = str(nav_list)

                        neighbor_list = eval(self.points_data.at[n_idx, 'Nav'])
                        neighbor_list.append(idx)
                        self.points_data.at[n_idx, 'Nav'] = str(neighbor_list)

            self.lines_layer = gpd.GeoDataFrame(lines, crs=self.points_data.crs)
            self.update_viewer()
            print(self.lines_layer)

    def update_coordinates(self, event): # Odświeżanie współrzędnych
        if event.xdata and event.ydata:
            self.status_bar.config(text=f'Współrzędne: ({event.xdata:.2f}, {event.ydata:.2f})')

    def zoom(self, event): # Zoomowanie
        scale = 0.8 if event.button == 'up' else 1.2
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata
        new_xlim = [xdata + (x - xdata) * scale for x in xlim]
        new_ylim = [ydata + (y - ydata) * scale for y in ylim]
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.canvas.draw()

    def start_pan(self, event): # Start przesuwania widoku
        if event.button == 1:  # LMB
            self.pan_active = True
            self.pan_start = (event.xdata, event.ydata)

    def pan(self, event): # Przesuwanie widoku
        if self.pan_active and event.xdata and event.ydata:
            dx = self.pan_start[0] - event.xdata
            dy = self.pan_start[1] - event.ydata
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.set_xlim([x + dx for x in xlim])
            self.ax.set_ylim([y + dy for y in ylim])
            self.canvas.draw()

    def end_pan(self, event): # Koniec przesuwania
        self.pan_active = False

    def toggle_manual_connect(self): # Przełącz tryb ręcznego dodawania połączeń
        self.manual_connect_mode = not self.manual_connect_mode
        self.manual_delete_mode = False
        self.selected_points = []
        self.update_buttons()

    def toggle_manual_delete(self): # Przełącz tryb ręcznego usuwania połączeń
        self.manual_delete_mode = not self.manual_delete_mode
        self.manual_connect_mode = False
        self.update_buttons()

    def update_buttons(self): # Zmiana tekstu przycisków narzędzi po aktywacji
        self.connect_button.config(text='Ręczne wybieranie połączeń (*)' if self.manual_connect_mode else 'Ręczne wybieranie połączeń')
        self.delete_button.config(text='Ręczne usuwanie połączeń (*)' if self.manual_delete_mode else 'Ręczne usuwanie połączeń')

    def on_click(self, event):
        if event.button == 3:
            if event.xdata and event.ydata:
                clicked_point = Point(event.xdata, event.ydata)
                # Tryb usuwania połączeń
                if self.manual_delete_mode and not self.lines_layer.empty:
                    distances = self.lines_layer.distance(clicked_point)
                    nearest_line = distances.idxmin()
                    if distances[nearest_line] < 5:
                        line_to_delete = self.lines_layer.loc[nearest_line]
                        from_id, to_id = int(line_to_delete['od']), int(line_to_delete['do'])  # Konwersja na int
                        self.lines_layer = self.lines_layer.drop(index=nearest_line)
                        # Dodanie atrybutów
                        if 'Nav' in self.points_data.columns:
                            for point_id in [from_id, to_id]:
                                if point_id in self.points_data.index:  # Sprawdzenie istnienia point_id
                                    nav_list = eval(self.points_data.at[point_id, 'Nav'])
                                    if point_id == from_id and to_id in nav_list:
                                        nav_list.remove(to_id)
                                    elif point_id == to_id and from_id in nav_list:
                                        nav_list.remove(from_id)
                                    self.points_data.at[point_id, 'Nav'] = str(nav_list)
                                else:
                                    print(f"Punkt o ID {point_id} nie istnieje w points_data.")
                        self.update_viewer()
                # Tryb dodawania połączeń
                if self.manual_connect_mode:
                    nearest_point = None
                    min_distance = float('inf')
                    # Punkt w pobliżu kliknięcia
                    for idx, point in self.points_data.iterrows():
                        distance = point.geometry.distance(clicked_point)
                        if distance < self.search_radius and distance < min_distance:
                            min_distance = distance
                            nearest_point = idx
                    if nearest_point is not None:
                        self.selected_points.append(nearest_point)

                    # Utworzenie połączenia po wybraniu dwóch punktów
                    if len(self.selected_points) == 2:
                        p1, p2 = self.selected_points
                        if p1 != p2:  # Sprawdzenie istnienia obecnego połączenia
                            p1_nav = eval(self.points_data.at[p1, 'Nav'])
                            p2_nav = eval(self.points_data.at[p2, 'Nav'])
                            if p2 not in p1_nav and p1 not in p2_nav:
                                line = LineString([self.points_data.geometry[p1], self.points_data.geometry[p2]])
                                new_line = {'geometry': line, 'od': p1, 'do': p2}
                                self.lines_layer = pd.concat(
                                    [self.lines_layer, gpd.GeoDataFrame([new_line], crs=self.lines_layer.crs)])
                                self.lines_layer = self.lines_layer.reset_index(drop=True)
                                # Aktualizacja atrybutów
                                p1_nav.append(p2)
                                p2_nav.append(p1)
                                self.points_data.at[p1, 'Nav'] = str(p1_nav)
                                self.points_data.at[p2, 'Nav'] = str(p2_nav)
                                self.update_viewer()
                        self.selected_points = []

    def check_intersections(self): # Zaznacz przecinające się połączenia
        if not self.lines_layer.empty:
            intersecting_lines = []
            for idx, line1 in self.lines_layer.iterrows():
                for jdx, line2 in self.lines_layer.iterrows():
                    if idx != jdx and line1.geometry.intersects(line2.geometry):
                        midpoint = line1.geometry.interpolate(0.5, normalized=True)
                        # Promień szukania przecinań
                        if line2.geometry.distance(midpoint) < float(self.intersection_input.get()):
                            intersecting_lines.append((idx, jdx))
            # Kolorowanie przecinających się linii
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            self.ax.cla()
            if self.help_layer is not None:
                self.help_layer.plot(ax=self.ax, color='green')
            if not self.lines_layer.empty:
                for idx, line in self.lines_layer.iterrows():
                    if any(idx in pair for pair in intersecting_lines):
                        color = f'#{randint(0, 255):02x}{randint(0, 255):02x}{randint(0, 255):02x}'
                        self.ax.plot(*line.geometry.xy, color=color, linewidth=3, linestyle='--')
                    else:
                        self.ax.plot(*line.geometry.xy, color='blue')
            if self.points_data is not None:
                self.points_data.plot(ax=self.ax, color='red')
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
            self.canvas.draw()

    def export_to_json(self): # Eksport do formatu JSON
        if self.lines_layer is not None and self.points_data is not None:
            points_file_name = self.point_lr.cget("text").split(": ")[1]
            lines_file_name = self.nazwa_navfile
            def export_gdf_to_json(gdf, file_name, file_suffix):
                file_path = filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON Files', '*.json')],title=f"Zapisz plik {file_suffix} JSON",initialfile=os.path.splitext(file_name)[0] + f".json")
                if file_path:
                    feature_collection = geojson.FeatureCollection(geojson.loads(gdf.to_json()))
                    output_json = {
                        "type": "FeatureCollection",
                        "name": os.path.splitext(file_name)[0],
                        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                        "xy_coordinate_resolution": 1e-08,
                        "features": feature_collection['features']
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(output_json, f, ensure_ascii=False, indent=4)
            export_gdf_to_json(self.lines_layer, lines_file_name, "linii navmesh")
            export_gdf_to_json(self.points_data, points_file_name, "punktów")

    def export_to_js(self):
        if self.lines_layer is not None and self.points_data is not None:
            points_file_name = self.point_lr.cget("text").split(": ")[1]
            lines_file_name = self.nazwa_navfile
            def export_gdf_to_js(gdf, file_name, file_suffix):
                file_path = filedialog.asksaveasfilename(defaultextension='.js',filetypes=[('JavaScript Files', '*.js')],title=f"Zapisz plik {file_suffix} JavaScript",initialfile=os.path.splitext(file_name)[0] + f".js")
                if file_path:
                    json_data = json.loads(gdf.to_json())
                    feature_collection = geojson.FeatureCollection(json_data['features'])
                    output_json = {
                        "type": "FeatureCollection",
                        "name": os.path.splitext(file_name)[0],
                        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                        "xy_coordinate_resolution": 1e-08,
                        "features": feature_collection['features']
                    }
                    file_name = os.path.splitext(os.path.basename(file_path))[0]
                    prefix = f"var json_{file_name} = "
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(prefix)
                        json.dump(output_json, f, ensure_ascii=False, indent=4)
            export_gdf_to_js(self.lines_layer, lines_file_name, "linii navmesh")
            export_gdf_to_js(self.points_data, points_file_name, "punktów")

    def save_layers(self): # Zapisz warstwy
        if self.lines_layer is not None:
            if 'fid' in self.lines_layer.columns:
                self.lines_layer = self.lines_layer.drop(columns=['fid'])
            if 'fid' in self.points_data.columns:
                self.points_data = self.points_data.drop(columns=['fid'])
            line_file = filedialog.asksaveasfilename(defaultextension='.gpkg',
                                                     filetypes=[('GeoPackage Files', '*.gpkg')],
                                                     title="Zapisz plik warstwy linii navmesh")
            if line_file:
                self.lines_layer.to_file(line_file, driver='GPKG')
                if 'fid' in self.points_data.columns:
                    self.points_data = self.points_data.drop(columns=['fid'])
                if 'ID' in self.points_data.columns:
                    self.points_data['ID'] = pd.to_numeric(self.points_data['ID'], errors='raise')
                point_file = filedialog.asksaveasfilename(defaultextension='.gpkg',
                                                          filetypes=[('GeoPackage Files', '*.gpkg')],
                                                          title="Zapisz plik zaktualizowanej warstwy punków")
                if point_file:
                    self.points_data.to_file(point_file, driver='GPKG')

# Odpalenie programu
if __name__ == '__main__':
    program = NavmeshApp()
    program.root.mainloop()
