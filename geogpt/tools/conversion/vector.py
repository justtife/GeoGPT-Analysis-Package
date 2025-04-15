import geopandas as gpd
from pathlib import Path
from typing import Optional
from ...utils.registry import register_function
from ...logger import GeoGPTLogger
import zipfile
import os
logger = GeoGPTLogger.get_logger(__name__)


class VectorConv:
    def __init__(self, wDir: str):
        self._wDir = Path(wDir).resolve()

    def _resolve_path(self, file_path: str) -> Path:
        path = Path(file_path)
        if not path.is_absolute():
            path = self._wDir / path
        resolved = path.resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Input file not found: {resolved}")
        return resolved

    def _extract_kmz(self, kmz_path: Path) -> Path:
        """Extract KMZ file to KML."""
        with zipfile.ZipFile(kmz_path, 'r') as kmz:
            kml_files = [f for f in kmz.namelist(
            ) if f.lower().endswith('.kml')]
            if not kml_files:
                raise ValueError("No KML file found in KMZ archive")
            kml_path = kmz.extract(kml_files[0], path=str(kmz_path.parent))
            return Path(kml_path)

    def _convert_vector_file(
        self,
        input_file: str,
        output_file: Optional[str],
        input_ext: str,
        output_ext: str,
        output_driver: str,
        allow_kmz: bool = False
    ) -> str:
        input_path = self._resolve_path(input_file)
        extracted_kml = None

        try:
            if allow_kmz and input_path.suffix.lower() == '.kmz':
                logger.info(f"Extracting KML from KMZ: {input_path}")
                extracted_kml = self._extract_kmz(input_path)
                input_path = extracted_kml

            if input_path.suffix.lower() != input_ext:
                raise ValueError(
                    f"Expected a {input_ext} file for this conversion.")

            output_path = Path(
                output_file) if output_file else input_path.with_suffix(output_ext)
            logger.info(
                f"Converting {input_ext.upper()} to {output_ext.upper()}: {input_path} → {output_path}")

            gdf = gpd.read_file(input_path)
            gdf.to_file(output_path, driver=output_driver)

            return str(output_path.resolve())

        finally:
            if extracted_kml and extracted_kml.exists():
                logger.info(f"Deleting extracted file: {extracted_kml}")
                os.remove(extracted_kml)

    # ---- Conversion Methods ----
    @register_function(name="kml_to_gpkg", description="", inputs=[], outputs=[], tags=[])
    def kml_to_gpkg(self, input_file: str, output_file: Optional[str] = None) -> str:
        return self._convert_vector_file(
            input_file, output_file,
            input_ext='.kml', output_ext='.gpkg',
            output_driver='GPKG',
            allow_kmz=True
        )

    @register_function(name="gpkg_to_kml", description="", inputs=[], outputs=[], tags=[])
    def gpkg_to_kml(self, input_file: str, output_file: Optional[str] = None) -> str:
        return self._convert_vector_file(
            input_file, output_file,
            input_ext='.gpkg', output_ext='.kml',
            output_driver='KML'
        )

    @register_function(name="shp_to_gpkg", description="", inputs=[], outputs=[], tags=[])
    def shp_to_gpkg(self, input_file: str, output_file: Optional[str] = None) -> str:
        input_path = self._resolve_path(input_file)
        # If directory was provided, find the .shp file
        if input_path.is_dir():
            shp_files = list(input_path.glob('*.shp'))
            if not shp_files:
                raise FileNotFoundError(
                    f"No .shp file found in directory: {input_path}")
            input_path = shp_files[0]

        # Verify this is a .shp file
        if input_path.suffix.lower() != '.shp':
            raise ValueError(f"Expected a .shp file, got: {input_path.suffix}")
        # Check for required companion files
        required_extensions = ['.shx', '.dbf', '.prj']
        missing_files = []
        for ext in required_extensions:
            companion_file = input_path.with_suffix(ext)
            if not companion_file.exists():
                missing_files.append(companion_file.name)

        if missing_files:
            raise FileNotFoundError(
                f"Shapefile components missing: {', '.join(missing_files)}\n"
                f"Required files: .shp, .shx, .dbf, .prj"
            )

        # Proceed with conversion
        return self._convert_vector_file(
            str(input_path), output_file,
            input_ext='.shp', output_ext='.gpkg',
            output_driver='GPKG'
        )

    @register_function(name="gpkg_to_shp", description="", inputs=[], outputs=[], tags=[])
    def gpkg_to_shp(self, input_file: str, output_file: Optional[str] = None) -> str:
        return self._convert_vector_file(
            input_file, output_file,
            input_ext='.gpkg', output_ext='.shp',
            output_driver='ESRI Shapefile'
        )

    @register_function(name="geojson_to_gpkg", description="", inputs=[], outputs=[], tags=[])
    def geojson_to_gpkg(self, input_file: str, output_file: Optional[str] = None) -> str:
        return self._convert_vector_file(
            input_file, output_file,
            input_ext='.geojson', output_ext='.gpkg',
            output_driver='GPKG'
        )

    @register_function(name="gpkg_to_geojson", description="", inputs=[], outputs=[], tags=[])
    def gpkg_to_geojson(self, input_file: str, output_file: Optional[str] = None) -> str:
        return self._convert_vector_file(
            input_file, output_file,
            input_ext='.gpkg', output_ext='.geojson',
            output_driver='GeoJSON'
        )

    # @register_function(name="dxf_to_shp")
    # @register_function(name="gpkg_to_shp")
    # @register_function(name="to_raster")
