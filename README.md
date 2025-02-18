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
- On `Mirror` mode, a synchronized map view panel is added, but panel position and size are to be set by user.
- On `Split` and `Lens` mode, a masking group layer `QMapCompare_Group` where comparing layers are duplicated in is added. Editing this group manually may cause unexpected visualization.



### Authors

- Raymond Lay ([@bordoray](https://github.com/bordoray)) - original author
- And all contributors

