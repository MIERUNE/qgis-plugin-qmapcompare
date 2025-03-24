# QMapCompare

<img src='./icon/icon.png' alt="QMapComparePlugin Icon" width="10%"><br>

A QGIS plugin that enables you to compare maps smoothly.

(QGIS version 3.34 and above is required)

<img src='./imgs/demo.gif' alt="QMapComparePlugin demo">
© OpenStreetMap Contributors
© Geospatial Information Authority of Japan

### Usage

- On left bottom panel, select comparing layers and click on one of the following buttons to start comparison:
  - <img src='./icon/compare_mirror.png' alt="QMapComparePlugin mirror Icon" width="5%"> Mirror
  - <img src='./icon/compare_split_vertical.png' alt="QMapComparePlugin vertical splitIcon" width="5%"> Vertical split
  - <img src='./icon/compare_split_horizontal.png' alt="QMapComparePlugin horizontal split Icon" width="5%"> Horizontal split
  - <img src='./icon/compare_lens.png' alt="QMapComparePlugin Lens Icon" width="5%"> Lens
- Map are updated on the fly when toggling comparing layers.
- Click on `Stop` button to end comparison.


### Notes
- On `Split` and `Lens` mode, a masking group layer `QMapCompare_Group` where comparing layers are duplicated in, is added. Editing this group manually may cause unexpected visualization.
- `Lens` mode may not work in case of data where rendering takes a while (e.g. high volume of data or layer which needs CRS transformation). It can be solved manually with one or more of the following methods:
  - (1) Set the project CRS to be the same as compare layers to avoid CRS transformation.
    - Setting the project CRS and converting compare layers to EPSG:3857 are highly recommended.
  - (2) Set lens rendering time interval.
    - Go to `QMapCompareMask` layer properties.
    - Rendering Tab -> Refresh Layer at Interval -> Set an interval time longer than 0.2s.
    - Lens comparison may not be efficient when interval exceeds 1 second in case of very huge and/or complex data.
  - (3) Reduce the volume and/or the complexity of rendering as following examples:
    - Convert CSV SHP etc. to GPKG
    - Filter to hide unused data
    - Simplify or split complex geometries

## More information
- [English](https://dev.to/mierune/seamlessly-compare-maps-on-qgis-with-the-qmapcompare-plugin-3186)
- [Japanese](https://qgis.mierune.co.jp/posts/howto_plugin_q-map-compare)

### Authors

- Raymond Lay ([@bordoray](https://github.com/bordoray)) - original author
- And all contributors

