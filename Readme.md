# Plugin QGIS - Raster Reclassifier
### Ver. 0.1
The plugin allows you to divide raster values into intervals using methods such as **Equal Interval** (intervals of equal width), **Quantile** (intervals based on quantiles), or **User** (manual interval definition). It is possible to customize the **colors** for the histogram and classes, making it easier to visually interpret the generated categories. The intervals can be modified, and table data can be saved in standard formats such as **CSV** or **TXT**. Additionally, the reclassified raster can be saved and automatically **loaded** into the QGIS project for further analysis. The plugin includes tools to display essential **statistics**, such as the count of valid cells, the mean, minimum, maximum, and standard deviation of the raster. It also allows **importing** interval values directly from external files. Thanks to its user-friendly interface, the plugin is suitable even for users with limited experience, enabling more in-depth analyses, such as creating thematic maps, identifying key areas, and categorizing data for specific purposes. By automating complex processes, it reduces the risk of errors and saves time. Its versatility makes it applicable in various fields, including environmental analysis, land management, and urban planning. Support for standard formats and direct integration with QGIS ensures compatibility with other tools and software, making this plugin a powerful and flexible solution for improving raster data analysis and presentation.

### Propriety

**Input Raster**:
>- Layer selection: Allows you to choose the raster layer loaded in the QGIS project for analysis.
>- Band: Lets you select the color band to use for extracting the raster intervals.
>- Extended: Defines the extent of the raster to analyze, with two options: "Full raster" to use the entire raster, and "Current view" to limit the analysis to the current project view.

**Color**:
> Allows you to define the colors for the raster histogram and the intervals defined during classification, making the different classes visually distinguishable.

**Classify**:
>	Method: Lets you choose the raster classification method:
>  - Equal Interval: Creates intervals of equal width.
>  - Quantile: Defines intervals based on quantiles.
>  - User: Allows you to manually define intervals, generating an empty table.
>
> Classes: Lets you set the number of classes to use during classification.
>
>	Extract: Extracts the intervals and displays them in the table, ready for use in the reclassification.

**Output raster**:
>- Save path: Displays the path where the newly reclassified raster file will be saved.
>- Output: Allows you to select the save path for the output file.
>- Load in QGIS: Lets you automatically load the reclassified raster into the QGIS project.

**Menu**:
>- Run: Executes the classification of the selected raster based on the defined parameters.
>- Cancel: Cancels the data calculated during the session.
>- Save Table: Allows you to save the table values to a CSV or TXT file.
>- Save Graph: Lets you save the histogram as an image.
>- Close: Closes the plugin window.

**Table**:
>- Displays the table with the defined intervals and columns for entering new values to be used for the raster reclassification.
>- Includes the statistical values of the raster (such as count, mean, minimum, maximum, and standard deviation).
>- Import: Lets you directly import interval values from a CSV or TXT file, populating the table with external data.

## Plugin Interface

![Img_1](https://github.com/user-attachments/assets/0ae39258-7024-4d2f-b304-2c5e9054c544)

![Img_2](https://github.com/user-attachments/assets/e1aefade-ade4-4e2a-aae9-704e245491e4)

![Img_3](https://github.com/user-attachments/assets/26e589f9-b580-40fe-8d08-1c5930426bb5)

![Img_4](https://github.com/user-attachments/assets/c9b74b51-5d07-4ce5-9723-3c9e02ffb85e)

![Img_5](https://github.com/user-attachments/assets/0c8de199-a3d1-4b2c-b1c8-60a373514ca3)
