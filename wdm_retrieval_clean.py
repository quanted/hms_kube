from __future__ import annotations

import argparse
import netrc
import os
import platform
import shutil
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from getpass import getpass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd

from cloud_cover_timeseries_from_solar import cloud_cover_timeseries_from_solar


CONSTITUENTS = ["ATEMP", "PRECIP", "SOLR", "WIND", "CLOU", "DEWP", "ATMP"]
EARTHDATA_HOST = "urs.earthdata.nasa.gov"


class EmptyLDASDataError(ValueError):
    """Raised when tsget returns no usable rows for a requested LDAS series."""

GLDAS_CONSTITUENT_DETAILS = {
    "PRECIP": ["Precipitation", "mm", "GLDAS2:GLDAS_NOAH025_3H_2_1_Rainf_f_tavg", "kg/m^2/s"],
    "ATEMP": ["Air Temperature", "Fahrenheit", "GLDAS2:GLDAS_NOAH025_3H_2_1_Tair_f_inst", "K"],
    "SOLR": ["Shortwave radiation flux", "Langleys", "GLDAS2:GLDAS_NOAH025_3H_2_1_SWdown_f_tavg", "W m-2"],
    "WIND": ["Wind Speed", "m s-1", "GLDAS2:GLDAS_NOAH025_3H_2_1_Wind_f_inst", "m s-1"],
    "CLOU": ["Cloud Cover Estimate", "Cloud Fraction", "GLDAS2:GLDAS_NOAH025_3H_2_1_SWdown_f_tavg", "W m-2"],
    "DEWP": [
        "Dewpoint temperature",
        "DegF",
        "GLDAS2:GLDAS_NOAH025_3H_2_1_Qair_f_inst",
        "GLDAS2:GLDAS_NOAH025_3H_2_1_Tair_f_inst",
        "GLDAS2:GLDAS_NOAH025_3H_2_1_PSurf_f_inst",
        "kg/kg",
        "K",
        "Pa",
    ],
    "ATMP": ["Sfc Pressure", "mmHg", "GLDAS2:GLDAS_NOAH025_3H_2_1_PSurf_f_inst", "Pa"],
}

NLDAS_CONSTITUENT_DETAILS = {
    "PRECIP": ["Precipitation", "mm", "NLDAS:NLDAS_FORA0125_H_2_0_Rainf", "mm"],
    "ATEMP": ["Air Temperature", "Fahrenheit", "NLDAS:NLDAS_FORA0125_H_2_0_Tair", "K"],
    "SOLR": ["Shortwave radiation flux", "Langleys", "NLDAS:NLDAS_FORA0125_H_2_0_SWdown", "W m-2"],
    "WIND": [
        "Wind Speed",
        "m s-1",
        "NLDAS:NLDAS_FORA0125_H_2_0_Wind_N",
        "NLDAS:NLDAS_FORA0125_H_2_0_Wind_E",
        "m s-1",
    ],
    "CLOU": ["Cloud Cover Estimate", "Cloud Fraction", "NLDAS:NLDAS_FORA0125_H_2_0_SWdown", "W m-2"],
    "DEWP": [
        "Dewpoint temperature",
        "DegF",
        "NLDAS:NLDAS_FORA0125_H_2_0_Qair",
        "NLDAS:NLDAS_FORA0125_H_2_0_Tair",
        "NLDAS:NLDAS_FORA0125_H_2_0_PSurf",
        "kg/kg",
        "K",
        "Pa",
    ],
    "ATMP": ["Surface Pressure", "mmHg", "NLDAS:NLDAS_FORA0125_H_2_0_PSurf", "Pa"]
}

US_BOUNDS = {
    "north": 49.3457868,
    "south": 24.7433195,
    "west": -124.7844079,
    "east": -66.9513812,
}


@dataclass(frozen=True)
class Station:
    name: str
    latitude: float
    longitude: float
    timezone_adjustment: float


@dataclass(frozen=True)
class RetrievalResult:
    series: pd.Series
    variable_name: str
    timestep_hours: int
    description: str
    column_name: str


def get_earthdata_auth_paths(target_dir: str | os.PathLike[str] | None = None) -> dict[str, Path]:
    base_dir = Path.home() if target_dir is None else Path(target_dir).expanduser().resolve()
    return {
        "base_dir": base_dir,
        "netrc": base_dir / ".netrc",
        "dodsrc": base_dir / ".dodsrc",
        "urs_cookies": base_dir / ".urs_cookies",
        "edl_token": base_dir / ".edl_token",
    }


def read_earthdata_credentials(
    netrc_path: str | os.PathLike[str],
    host: str = EARTHDATA_HOST,
) -> tuple[str, str] | None:
    path = Path(netrc_path)
    if not path.exists():
        return None

    try:
        auth = netrc.netrc(str(path))
        authenticators = auth.authenticators(host)
    except (FileNotFoundError, netrc.NetrcParseError, OSError, TypeError, ValueError):
        return None

    if not authenticators:
        return None

    username, _, password = authenticators
    if not username or not password:
        return None
    return username, password


def ensure_earthdata_credentials(
    target_dir: str | os.PathLike[str] | None = None,
    search_dirs: Iterable[str | os.PathLike[str]] | None = None,
    prompt_if_missing: bool = True,
    include_default_search_dirs: bool = True,
    input_func: Callable[[str], str] = input,
    password_func: Callable[[str], str] = getpass,
    host: str = EARTHDATA_HOST,
) -> dict[str, Path | bool | str | None]:
    """
    Reuse existing Earthdata auth files when available; otherwise prompt for credentials.

    The function always ensures `.urs_cookies` and `.dodsrc` exist in `target_dir`,
    and it keeps the active `.netrc` in that same location so downstream tools can
    find a consistent set of files.
    """
    paths = get_earthdata_auth_paths(target_dir)
    base_dir = paths["base_dir"]
    base_dir.mkdir(parents=True, exist_ok=True)

    raw_search_dirs: list[str | os.PathLike[str]] = [base_dir, *(search_dirs or [])]
    if include_default_search_dirs:
        raw_search_dirs.extend([Path.cwd(), Path.home()])

    unique_search_dirs: list[Path] = []
    for raw_dir in raw_search_dirs:
        candidate = Path(raw_dir).expanduser().resolve()
        if candidate not in unique_search_dirs:
            unique_search_dirs.append(candidate)

    prompted = False
    source_netrc: Path | None = None
    credentials: tuple[str, str] | None = None

    for directory in unique_search_dirs:
        candidate_netrc = directory / ".netrc"
        credentials = read_earthdata_credentials(candidate_netrc, host=host)
        if credentials:
            source_netrc = candidate_netrc
            break

    if credentials and source_netrc and source_netrc.resolve() != paths["netrc"].resolve():
        shutil.copyfile(source_netrc, paths["netrc"])

    if not credentials:
        if not prompt_if_missing:
            raise ValueError(
                "No usable Earthdata credentials were found in .netrc. "
                "Create a .netrc file or allow prompting."
            )

        username = input_func(
            "Enter NASA Earthdata Login Username "
            "(or create an account at urs.earthdata.nasa.gov): "
        ).strip()
        password = password_func("Enter NASA Earthdata Login Password: ").strip()

        if not username or not password:
            raise ValueError("Earthdata username and password are required.")

        paths["netrc"].write_text(
            f"machine {host} login {username} password {password}",
            encoding="utf-8",
        )
        credentials = (username, password)
        prompted = True

    if platform.system() != "Windows" and paths["netrc"].exists():
        os.chmod(paths["netrc"], 0o600)

    paths["urs_cookies"].touch(exist_ok=True)
    paths["dodsrc"].write_text(
        f"HTTP.COOKIEJAR={paths['urs_cookies']}\nHTTP.NETRC={paths['netrc']}",
        encoding="utf-8",
    )

    for directory in unique_search_dirs:
        candidate_token = directory / ".edl_token"
        if candidate_token.exists() and candidate_token != paths["edl_token"]:
            shutil.copyfile(candidate_token, paths["edl_token"])
            break

    return {
        "base_dir": base_dir,
        "netrc_path": paths["netrc"],
        "dodsrc_path": paths["dodsrc"],
        "urs_cookies_path": paths["urs_cookies"],
        "edl_token_path": paths["edl_token"] if paths["edl_token"].exists() else None,
        "username": credentials[0],
        "prompted": prompted,
    }


def validate_lat_lon(latitude: float, longitude: float) -> bool:
    return -90 <= float(latitude) <= 90 and -180 <= float(longitude) <= 180


def load_stations(csv_path: str | os.PathLike[str]) -> list[Station]:
    station_df = pd.read_csv(csv_path)
    required_columns = ["StationName", "Latitude", "Longitude", "TimeZoneAdjustment"]
    missing = [column for column in required_columns if column not in station_df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    stations: list[Station] = []
    for _, row in station_df.iterrows():
        if not validate_lat_lon(row["Latitude"], row["Longitude"]):
            raise ValueError(
                f"Invalid coordinates for station {row['StationName']}: "
                f"{row['Latitude']}, {row['Longitude']}"
            )
        stations.append(
            Station(
                name=str(row["StationName"]),
                latitude=float(row["Latitude"]),
                longitude=float(row["Longitude"]),
                timezone_adjustment=float(row["TimeZoneAdjustment"]),
            )
        )
    return stations


def in_contiguous_usa(station: Station) -> bool:
    return (
        US_BOUNDS["south"] < station.latitude < US_BOUNDS["north"]
        and US_BOUNDS["west"] < station.longitude < US_BOUNDS["east"]
    )


def get_catalog(station: Station) -> tuple[dict[str, list[str]], int, str]:
    if in_contiguous_usa(station):
        return NLDAS_CONSTITUENT_DETAILS, 1, "NLDAS"
    return GLDAS_CONSTITUENT_DETAILS, 3, "GLDAS"


def normalize_series(data: pd.Series | pd.DataFrame, name: str) -> pd.Series:
    if isinstance(data, pd.DataFrame):
        if data.shape[1] == 0:
            raise ValueError("Retrieved DataFrame has no columns.")
        series = data.iloc[:, 0].copy()
    elif isinstance(data, pd.Series):
        series = data.copy()
    else:
        raise TypeError(f"Expected pandas Series/DataFrame, got {type(data).__name__}")

    series.index = pd.to_datetime(series.index)
    series = pd.to_numeric(series, errors="coerce")
    series = series.dropna().sort_index()
    series.name = name
    return series


@lru_cache(maxsize=1)
def _get_tsget_module():
    from tsgettoolbox import tsgettoolbox as tsget

    return tsget


@lru_cache(maxsize=1)
def _get_wdm_module():
    from wdmtoolbox import wdmtoolbox as wdm

    return wdm


def convertunitforHSPF(constituent: str, series: pd.Series, ldas_var: str) -> pd.Series:
    series = normalize_series(series, constituent)

    if constituent == "ATEMP":
        series = ((series - 273.15)* 9.0 / 5.0) + 32.0 #new adjustments for farhenheit from celcius
    elif constituent == "SOLR":
        series = series * 0.0864 #TODO insert time zone conversion
    elif constituent == "PRECIP" and "GLDAS" in ldas_var:
        series = series * 3600 * 3
    elif constituent == "PRECIP" and "NLDAS" in ldas_var:
        series = series #TODO
    series.name = constituent
    return series


def compute_cloud_cover(solr_series: pd.Series, lat_deg: float) -> pd.Series:
    solr_series = normalize_series(solr_series, "SOLR")
    solr_series = convertunitforHSPF("SOLR", solr_series, "SOLR")
    clou_df = cloud_cover_timeseries_from_solar(
        solr_values=solr_series.tolist(),
        dates=solr_series.index.to_pydatetime().tolist(),
        lat_deg=lat_deg,
    )
    clou_series = normalize_series(clou_df, "CLOU")
    clou_series.name = "CLOU"
    return clou_series

def compute_dewpoint(
    spec_humidity_series: pd.Series,
    air_temp_series: pd.Series,
    pressure_series: pd.Series | None = None,
    default_pressure_mb: float = 1013.25,
) -> pd.Series:
    """
    Compute dew point temperature (deg F) from specific humidity and air temperature.

    The implementation follows the notebook formula used earlier in this workspace:
    - specific humidity in kg/kg
    - air temperature in K
    - pressure in Pa when provided, otherwise a default pressure in millibars
    - output dew point in deg F
    """
    spec_humidity_series = normalize_series(spec_humidity_series, "SPCHUM")
    air_temp_series = normalize_series(air_temp_series, "ATEMP")

    aligned = pd.concat(
        [
            spec_humidity_series.rename("SPCHUM"),
            air_temp_series.rename("ATEMP"),
        ],
        axis=1,
        join="inner",
    ).dropna()

    if pressure_series is not None:
        pressure_series = normalize_series(pressure_series, "ATMP")
        aligned = aligned.join(pressure_series.rename("ATMP"), how="inner").dropna()
        pressure_mb = aligned["ATMP"] / 100.0
    else:
        pressure_mb = pd.Series(default_pressure_mb, index=aligned.index, dtype=float)

    if aligned.empty:
        raise ValueError("No overlapping specific humidity and air temperature data are available for DEWP.")

    air_temp_c = aligned["ATEMP"] - 273.15
    saturation_vapor_pressure = 6.112 * np.exp((17.67 * air_temp_c) / (air_temp_c + 243.5))
    vapor_pressure = (
        aligned["SPCHUM"] * pressure_mb
        / (0.378 * aligned["SPCHUM"] + 0.622)
    )
    relative_humidity = (vapor_pressure / saturation_vapor_pressure).clip(lower=0.0, upper=1.0)
    dew_temp_c = air_temp_c - ((100.0 - 100.0 * relative_humidity) / 5.0)
    dewpoint_series = (dew_temp_c * 9.0 / 5.0) + 32.0
    dewpoint_series.name = "DEWP"
    return dewpoint_series.sort_index()

def compute_sfc_pressure(atmp_series: pd.Series) -> pd.Series:
    #placeholder for surface pressure calculation using atmp_series
    sfc_pressure_series = atmp_series * 0.000750062 # Implementation converting Pa to mmHg
    sfc_pressure_series.name = "ATMP"
    return sfc_pressure_series


def fetch_ldas_series(station: Station, variable_name: str, start_date: str, end_date: str) -> pd.Series:
    tsget = _get_tsget_module()
    result = tsget.ldas(
        lat=station.latitude,
        lon=station.longitude,
        variables=variable_name,
        startDate=start_date,
        endDate=end_date,
    )

    if isinstance(result, pd.Series) and result.empty:
        raise EmptyLDASDataError(
            "LDAS request returned no rows for "
            f"station '{station.name}' ({station.latitude}, {station.longitude}), "
            f"variable '{variable_name}', and date range {start_date} to {end_date}. "
            "This usually means the upstream tsget/Earthdata request returned an empty "
            "response. Verify your Earthdata login files (~/.netrc, ~/.dodsrc, ~/.urs_cookies), "
            "confirm the selected dataset/date range is available, and test tsget.ldas(...) "
            "directly in the same environment."
        )

    if isinstance(result, pd.DataFrame) and result.empty:
        raise EmptyLDASDataError(
            "LDAS request returned no rows for "
            f"station '{station.name}' ({station.latitude}, {station.longitude}), "
            f"variable '{variable_name}', and date range {start_date} to {end_date}. "
            "This usually means the upstream tsget/Earthdata request returned an empty "
            "response. Verify your Earthdata login files (~/.netrc, ~/.dodsrc, ~/.urs_cookies), "
            "confirm the selected dataset/date range is available, and test tsget.ldas(...) "
            "directly in the same environment."
        )

    series = normalize_series(result, variable_name)
    if series.empty:
        raise EmptyLDASDataError(
            "LDAS request returned rows, but no usable numeric values remained after cleanup for "
            f"station '{station.name}', variable '{variable_name}', and date range {start_date} to {end_date}."
        )
    return series


def build_result_for_constituent(
    station: Station,
    constituent: str,
    start_date: str,
    end_date: str,
) -> RetrievalResult:
    catalog, timestep_hours, dataset_name = get_catalog(station)

    if constituent == "WIND" and dataset_name == "NLDAS":
        wind_n_var = catalog["WIND"][2]
        wind_e_var = catalog["WIND"][3]
        wind_n = fetch_ldas_series(station, wind_n_var, start_date, end_date)
        wind_e = fetch_ldas_series(station, wind_e_var, start_date, end_date)
        wind_n, wind_e = wind_n.align(wind_e, join="inner")
        wind_speed = np.sqrt(wind_n.pow(2) + wind_e.pow(2))
        wind_speed = normalize_series(wind_speed, "WIND")
        return RetrievalResult(
            series=wind_speed,
            variable_name=f"{wind_n_var} + {wind_e_var}",
            timestep_hours=timestep_hours,
            description="Vector Wind Speed",
            column_name="WIND",
        )

    if constituent == "CLOU":
        solar_var = catalog["CLOU"][2]
        solr_series = fetch_ldas_series(station, solar_var, start_date, end_date)
        clou_series = compute_cloud_cover(solr_series, station.latitude)
        return RetrievalResult(
            series=clou_series,
            variable_name=solar_var,
            timestep_hours=timestep_hours,
            description=solar_var,
            column_name="CLOU",
        )
    if constituent == "DEWP":
        spec_humidity_var = catalog["DEWP"][2]
        air_temp_var = catalog["DEWP"][3]
        pressure_var = catalog["DEWP"][4] if len(catalog["DEWP"]) > 4 else None

        spec_humidity_series = fetch_ldas_series(station, spec_humidity_var, start_date, end_date)
        air_temp_series = fetch_ldas_series(station, air_temp_var, start_date, end_date)
        pressure_series = (
            fetch_ldas_series(station, pressure_var, start_date, end_date)
            if pressure_var
            else None
        )

        dewpoint_series = compute_dewpoint(
            spec_humidity_series,
            air_temp_series,
            pressure_series=pressure_series,
        )
        variable_name = f"{spec_humidity_var} + {air_temp_var}"
        if pressure_var:
            variable_name = f"{variable_name} + {pressure_var}"

        return RetrievalResult(
            series=dewpoint_series,
            variable_name=variable_name,
            timestep_hours=timestep_hours,
            description="Computed dewp from q, air temp, and pressure",
            column_name="DEWP",
        )
    if constituent == "ATMP":
        atmp_var = catalog["ATMP"][2]
        sfcp_series = fetch_ldas_series(station, atmp_var, start_date, end_date)
        atmp_series = compute_sfc_pressure(sfcp_series)
        return RetrievalResult(
            series=atmp_series,
            variable_name=atmp_var,
            timestep_hours=timestep_hours,
            description=atmp_var,
            column_name="ATMP",
        )#TODO
    variable_name = catalog[constituent][2]
    series = fetch_ldas_series(station, variable_name, start_date, end_date)
    series = convertunitforHSPF(constituent, series, variable_name)
    description = "Vector Wind Speed" if constituent == "WIND" and dataset_name == "NLDAS" else variable_name
    return RetrievalResult(
        series=series,
        variable_name=variable_name,
        timestep_hours=timestep_hours,
        description=description,
        column_name=constituent,
    )


def prepare_wdm_input(series: pd.Series, constituent: str) -> pd.DataFrame:
    series = normalize_series(series, constituent)
    if series.empty:
        raise ValueError(f"No data available to write for constituent {constituent}.")
    return series.to_frame(name=constituent)


def write_result_to_wdm(
    wdm_path: str | os.PathLike[str],
    dsn: int,
    station: Station,
    constituent: str,
    result: RetrievalResult,
) -> None:
    wdm = _get_wdm_module()
    input_df = prepare_wdm_input(result.series, constituent)
    wdm.createnewdsn(
        str(wdm_path),
        dsn,
        constituent=constituent,
        scenario="OBSERVED",
        location=station.name[:8],
        tcode=3,
        statid=station.name,
        tsstep=result.timestep_hours,
        description=result.description,
    )
    wdm.csvtowdm(str(wdm_path), dsn, input_ts=input_df)


def derive_log_path(wdm_path: str | os.PathLike[str], explicit_log_path: str | None = None) -> Path:
    if explicit_log_path:
        return Path(explicit_log_path)
    wdm_path = Path(wdm_path)
    return wdm_path.with_name(wdm_path.stem.replace("MetData", "MetLog") + ".txt")


def run_retrieval(
    stations: Iterable[Station],
    start_date: str,
    end_date: str,
    wdm_path: str | os.PathLike[str],
    log_path: str | os.PathLike[str] | None = None,
) -> tuple[Path, Path]:
    wdm = _get_wdm_module()
    ensure_earthdata_credentials()

    wdm_path = Path(wdm_path).resolve()
    log_path = derive_log_path(wdm_path, None if log_path is None else str(log_path)).resolve()

    wdm.createnewwdm(str(wdm_path), overwrite=True)
    dsn = 1

    with open(log_path, "w", encoding="utf-8") as logfile:
        logfile.write(
            "Started downloading data at "
            f"{datetime.now().isoformat()} and saving in {wdm_path.name}\n"
        )

        for station in stations:
            logfile.write(
                f"Station: {station.name}, Latitude: {station.latitude}, "
                f"Longitude: {station.longitude}, TimeZoneAdjustment: {station.timezone_adjustment}\n"
            )

            for constituent in CONSTITUENTS:
                try:
                    result = build_result_for_constituent(
                        station=station,
                        constituent=constituent,
                        start_date=start_date,
                        end_date=end_date,
                    )
                    write_result_to_wdm(wdm_path, dsn, station, constituent, result)
                    logfile.write(
                        f"Constituent: {constituent}, Column Name: {result.column_name}, DSN: {dsn}\n"
                    )
                    dsn += 1
                except EmptyLDASDataError as exc:
                    logfile.write(f"ERROR for {constituent}: {exc}\n")
                    raise

    return wdm_path, log_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrieve NLDAS/GLDAS time series and write them to a WDM file."
    )
    parser.add_argument(
        "--stations",
        default="station_example.csv",
        help="CSV file with StationName, Latitude, Longitude, TimeZoneAdjustment columns.",
    )
    parser.add_argument("--start-date", required=True, help="Start date in YYYY-MM-DD format.")
    parser.add_argument("--end-date", required=True, help="End date in YYYY-MM-DD format.")
    parser.add_argument("--wdm-file", default="MetData_clean.wdm", help="Output WDM file path.")
    parser.add_argument("--log-file", default=None, help="Optional explicit MetLog output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stations = load_stations(args.stations)
    wdm_path, log_path = run_retrieval(
        stations=stations,
        start_date=args.start_date,
        end_date=args.end_date,
        wdm_path=args.wdm_file,
        log_path=args.log_file,
    )
    print(f"Created WDM file: {wdm_path}")
    print(f"Created log file: {log_path}")


if __name__ == "__main__":
    main()


