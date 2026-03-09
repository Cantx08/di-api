import io
from typing import Dict
from matplotlib import pyplot as plt
import matplotlib
from ...domain.report_repository import IChartGenerator


matplotlib.use('Agg')  # Use non-interactive backend

class MatplotlibChartGenerator(IChartGenerator):
    """Implementación de generador de gráficos usando matplotlib."""
    
    def __init__(self):
        self._configure_matplotlib()
    
    @staticmethod
    def _configure_matplotlib() -> None:
        """Configura matplotlib con ajustes por defecto."""
        plt.style.use('default')
    
    def generate_line_chart(self, documents_by_year: Dict[str, int], author_name: str) -> bytes:
        """Genera un gráfico de tendencias por año."""
        # Crear figura
        plt.figure(figsize=(8, 4))
        
        # Preparar datos
        years = sorted([int(year) for year in documents_by_year.keys()])
        counts = [documents_by_year[str(year)] for year in years]
        
        # Crear gráfico de línea con colores personalizados
        plt.plot(years, counts, marker='o', linewidth=2, markersize=6, color='#009ece')
        
        # Configurar etiquetas y título
        plt.xlabel('Year', fontsize=10, ha='center', color='#2e2e2e')
        plt.ylabel('Documents', fontsize=10, ha='center', color='#2e2e2e')
        plt.title('Documents by year', fontsize=13, pad=15, color='#2e2e2e', loc='left')
        
        # Configurar grid - solo líneas horizontales
        plt.grid(axis='y', alpha=0.3, color='#cccccc')
        
        # Hacer transparentes los bordes de la gráfica
        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        
        # Eliminar márgenes
        plt.margins(0)
        plt.tight_layout(pad=0)
        
        # Configurar límites de ejes
        plt.xlim(min(years) - 0.5, max(years) + 0.5)
        plt.ylim(0, max(counts) + 1)
        
        # Configurar ticks dinámicamente según la cantidad de datos
        # X-axis (años): determinar el paso según el rango de años
        year_range = max(years) - min(years) + 1
        if year_range <= 15:
            # Pocas publicaciones: mostrar todos los años
            x_step = 1
        elif year_range <= 30:
            # Rango medio: mostrar cada 2 años
            x_step = 2
        elif year_range <= 45:
            # Rango grande: mostrar cada 3 años
            x_step = 3
        else:
            # Rango muy grande: mostrar cada 5 años
            x_step = 5
        
        x_ticks = list(range(min(years), max(years) + 1, x_step))
        plt.xticks(x_ticks, color='#2e2e2e')
        
        # Y-axis (número de publicaciones): determinar el paso según el máximo
        max_count = max(counts) if counts else 1
        if max_count <= 5:
            # Pocas publicaciones: mostrar de 1 en 1
            y_step = 1
        elif max_count <= 10:
            # Cantidad media: mostrar de 2 en 2
            y_step = 2
        elif max_count <= 20:
            # Cantidad considerable: mostrar de 5 en 5
            y_step = 3
        else:
            # Muchas publicaciones: mostrar de 10 en 10
            y_step = 5
        
        y_ticks = list(range(0, max_count + y_step + 1, y_step))
        plt.yticks(y_ticks, color='#2e2e2e')
        
        # Guardar como imagen
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer.getvalue()
