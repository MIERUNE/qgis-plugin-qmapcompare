# Compare layers and group names
compare_group_name = "QMapCompare_Group"
compare_mask_layer_name = "QMapCompareMask"
compare_background_layer_name = "QMapCompareBackground"

# Lens compare parameters
lens_default_size_rate = 0.15
lens_min_size_rate = 0.05
lens_max_size_rate = 0.40
# - lens dynamic refresh interval: 200 milliseconds = 0.2s
lens_auto_refresh_interval_time = 200

# Geometry generator formula for compare masks
vertical_split_geometry = """make_rectangle_3points(
        make_point(x(@map_extent_center), y(@map_extent_center) - (@map_extent_height / 2)),
        make_point(x(@map_extent_center), y(@map_extent_center) + (@map_extent_height / 2)),
        make_point(x(@map_extent_center) + (@map_extent_width / 2), y(@map_extent_center) + (@map_extent_height / 2)),
        0)"""

horizontal_split_geometry = """make_rectangle_3points(
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center)),
        make_point(x(@map_extent_center) + (@map_extent_width / 2), y(@map_extent_center) ),
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center) - (@map_extent_height / 2)),
        0)"""

def get_lens_geometry(shape: str = "circle", rate: float = lens_default_size_rate) -> str:
    """Generate lens geometry expression for the given shape and size rate."""
    rate = max(lens_min_size_rate, min(lens_max_size_rate, rate))
    if shape == "square":
        cx = "x(@canvas_cursor_point)"
        cy = "y(@canvas_cursor_point)"
        offset = f"@map_extent_width * {rate}"
        bottom_left = f"make_point({cx} - {offset}, {cy} - {offset})"
        top_left = f"make_point({cx} - {offset}, {cy} + {offset})"
        top_right = f"make_point({cx} + {offset}, {cy} + {offset})"
        return f"make_rectangle_3points({bottom_left}, {top_left}, {top_right}, 0)"
    return f"buffer(@canvas_cursor_point, @map_extent_width * {rate})"

compare_background_geometry = """@map_extent"""

# Mirror compare related constants
mirror_widget_name = "QMapCompare Mirror"
mirror_maptheme_name = "QMapCompare Mirror"
