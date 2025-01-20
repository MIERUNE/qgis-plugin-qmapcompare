compare_group_name = "QMapCompare_Group"
compare_mask_layer_name = "QMapCompareMask"

horizontal_split_geometry = """make_rectangle_3points(
        make_point(x(@map_extent_center), y(@map_extent_center) - (@map_extent_height / 2)),
        make_point(x(@map_extent_center), y(@map_extent_center) + (@map_extent_height / 2)),
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center) + (@map_extent_height / 2)),
        0)"""

vertical_split_geometry = """make_rectangle_3points(
        make_point(x(@map_extent_center), y(@map_extent_center) - (@map_extent_width / 2)),
        make_point(x(@map_extent_center), y(@map_extent_center) + (@map_extent_width / 2)),
        make_point(x(@map_extent_center) - (@map_extent_width / 2), y(@map_extent_center) + (@map_extent_height / 2)),
        0)"""