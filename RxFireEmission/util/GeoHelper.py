import fiona
from shapely.geometry import shape


def StatePolygon(state_name):
    """
    List of States:
        Maryland, Iowa, Delaware, Ohio, Pennsylvania, Nebraska, Washington, Puerto Rico, Alabama,
        Arkansas, New Mexico, Texas, California, Kentucky, Georgia, Wisconsin, Oregon,
        Missouri, Virginia, Tennessee, Louisiana, New York, Michigan, Idaho, Florida,
        Alaska, Illinois, Montana, Minnesota, Indiana, Massachusetts, Kansas, Nevada,
        Vermont, Connecticut, New Jersey, District of Columbia, North Carolina, Utah,
        North Dakota, South Carolina, Mississippi, Colorado, South Dakota, Oklahoma,
        Wyoming, West Virginia, Maine, Hawaii, New Hampshire, Arizona, Rhode Island
    :param state_name: input the state name in the list
    :return: polygon of the state
    """
    us_shape_name = "/Users/zongrunli/Desktop/RxFireEmission/data/geo_data/US/cb_2018_us_state_20m.shp"
    us_states = fiona.open(us_shape_name)
    state_geo = None
    for us_state in us_states:
        cur_name = us_state['properties']['NAME']
        if state_name == cur_name:
            state_geo = shape(us_state['geometry'])
            break
    return state_geo


def FederalLand(state_name):
    """

    :param state_name: Georgia, Florida, South Carolina
    :return: polygon of the state
    """
    filename = "/Users/zongrunli/Desktop/RxFireEmission/data/geo_data/FederalLand/fedlanp010g.shp"
    GA = ['GA', 'AL-GA', 'NC-SC-GA', 'GA-NC', 'GA-TN']
    FL = ['FL']
    SC = ['SC', 'NC-SC-GA']
    state_name_list = None
    if state_name == "Georgia":
        state_name_list = GA
    elif state_name == "Florida":
        state_name_list = FL
    elif state_name == "South Carolina":
        state_name_list = SC
    federal_land = fiona.open(filename)
    result_polygon = []
    for land in federal_land:
        state = land["properties"]['STATE']
        if state in state_name_list:
            result_polygon.append(shape(land['geometry']))
    return result_polygon


def county(state_name):
    filename = "/Users/zongrunli/Desktop/RxFireEmission/data/geo_data/County/tl_2021_us_county.shp"
    state_fp = {"Alabama": '01', "Georgia": '13', "Tennessee": '47', "Florida": '12',
                           "Mississippi": '28', "North Carolina": '37', "South Carolina": '45',
                           "Arkansas": '05', "Louisiana": '22', "Kentucky": '21', "Virginia": '51',
                           "West Virginia": '54'}
    us_counties = fiona.open(filename)
    counties = []
    county_codes = []
    state_number = state_fp[state_name]
    for us_county in us_counties:
        county_state = us_county['properties']['STATEFP']
        county_code = us_county['properties']['COUNTYNS']
        if county_state == state_number:
            county_geo = shape(us_county['geometry'])
            counties.append(county_geo)
            county_codes.append(county_code)
    return county_codes, counties