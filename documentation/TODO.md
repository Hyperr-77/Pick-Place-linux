# TODO

## Database class

- [X] Add a new bin table that holds a cluster and a bin position
- [X] Add a add_bin(center_x, center_y) function
- [X] Add a remove_bin(bin_id) function
- [X] Add a subscribe_bin(cluster_id) function
- [X] Add a unsubscribe_bin(cluster_id) function
- [X] Add a get_bin(cluster_id) function
- [X] Add a new UI table that holds a cluster id, a preview image, an image of the whole plate with the object and a cluster id (from cluster table)
- [X] Add a stream_ui() function that streams all UI preview images in the UI table
- [X] Add a add_ui(cluster_id, prev_image, full_image) function
- [X] Add a remove_ui(ui_id)
- [X] Add a get_ui(ui_id) function that gets all UI data of the id
- [X] Remove a cluster's bin assignment and saved UI images when deleting the cluster
- [X] Store each example's matching background image and migrate existing UI tables

## UI class

- [ ] Create UI class
- [ ] Replace placeholders with the full-window camera, crop configuration, and database editing views
- [ ] Add a remove_cluster(ui_id) function that unsubscribes its bin and removes the cluster and associated data

## Robot class

- [ ] Implement all functions defined in documentation.md (found in older version of this project)
- [ ] Implement needed lower-level functions for the other functions to work
- [ ] Add the pixel_to_real_coordinate(pixel_x, pixel_y) function from documentation.md

## classify.py

- [X] Save preview and full-frame UI images when classification creates a cluster
- [X] Validate rectangle and feature-vector counts

## TODO.md

- [ ] Update TODO.md to reflect completed database, UI, and classification work


## README.md

- [ ] Finish the readme (tutorial: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

## pyproject.toml

- [ ] Add project url from github when uploaded