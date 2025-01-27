compare_group_name = "QMapCompare_Group"
compare_mask_layer_name = "QMapCompareMask"

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

# lens radius is 15% of the map extent width
lens_geometry = "buffer(@canvas_cursor_point, @map_extent_width * 0.15)"
