import pytest
import os
import shutil
from datetime import datetime, timedelta
from src.domain.models import EnergyReading, EnergySeries
from src.adapters.graph_plotter import GraphPlotter

@pytest.fixture
def sample_series():
    readings = []
    base_time = datetime(2023, 1, 1, 0, 0)
    for i in range(24):
        readings.append(EnergyReading(
            base_time + timedelta(hours=i),
            10.0 + i,
            5.0 + (i/2)
        ))
    return EnergySeries(readings)

@pytest.fixture
def output_dir():
    dir_path = "test_output_graphs"
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    os.makedirs(dir_path)
    yield dir_path
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def test_generate_graphs(sample_series, output_dir):
    plotter = GraphPlotter()
    files = plotter.generate_graphs(sample_series, output_dir)
    
    assert len(files) > 0
    for f in files:
        assert os.path.exists(f)
        assert f.endswith(".png")
        
    # Test with custom filename
    custom_name = "custom_plot.png"
    files_custom = plotter.generate_graphs(sample_series, output_dir, output_file=custom_name)
    assert len(files_custom) > 0
    assert files_custom[0].endswith(custom_name)
    assert os.path.exists(os.path.join(output_dir, custom_name))

    # Test smoothing (rolling)
    files_rolling = plotter.generate_graphs(sample_series, output_dir, output_file="rolling.png", 
                                           smoothing_method="rolling", smoothing_param=3)
    assert len(files_rolling) > 0
    assert os.path.exists(os.path.join(output_dir, "rolling.png"))
    
    # Test smoothing (spline)
    files_spline = plotter.generate_graphs(sample_series, output_dir, output_file="spline.png", 
                                          smoothing_method="spline")
    assert len(files_spline) > 0
    assert os.path.exists(os.path.join(output_dir, "spline.png"))
