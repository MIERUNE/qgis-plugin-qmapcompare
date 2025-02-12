# Compare layers and group names
compare_group_name = "QMapCompare_Group"
compare_mask_layer_name = "QMapCompareMask"
compare_background_layer_name = "QMapCompareBackground"

# Lens compare parameters
# - lens radius is 15% of the map extent width
lens_size_rate_from_map_canvas = 0.15
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

lens_geometry = f"buffer(@canvas_cursor_point, @map_extent_width * {lens_size_rate_from_map_canvas})"

compare_background_geometry = """@map_extent"""

# Mirror compare related constants
mirror_widget_name = "QMapCompare Mirror"
mirror_maptheme_name = "QMapCompare Mirror"