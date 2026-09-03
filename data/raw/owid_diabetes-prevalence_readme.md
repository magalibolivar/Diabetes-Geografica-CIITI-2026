# Share of people with diabetes - Data package

This data package contains the data that powers the chart ["Share of people with diabetes"](https://ourworldindata.org/grapher/diabetes-prevalence?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website. It was downloaded on September 3, 2026.

### Active Filters

A filtered subset of the full data was downloaded. The following filters were applied:

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For most countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The final column is the data column, which is the time series that powers the chart. If the CSV data is downloaded using the "full data" option, then the column corresponds to the time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data column is transformed depending on the chart type and thus the association with the time series might not be as straightforward.


## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

## Detailed information about the data


## Diabetes prevalence (% of population ages 20 to 79)
Last updated: July 27, 2026  
Next update: January 2027  
Date range: 2000–2024  
Unit: % of population ages 20 to 79  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
International Diabetes Federation (Diabetes Atlas), via World Bank (2026) – processed by Our World in Data

#### Full citation
International Diabetes Federation (Diabetes Atlas), via World Bank (2026) – processed by Our World in Data. “Diabetes prevalence (% of population ages 20 to 79)” [dataset]. International Diabetes Federation (Diabetes Atlas), via World Bank, “World Development Indicators 129” [original data].
Source: International Diabetes Federation (Diabetes Atlas), via World Bank (2026) – processed by Our World in Data

### How is this data described by its producer - International Diabetes Federation (Diabetes Atlas), via World Bank (2026)?
Diabetes prevalence refers to the percentage of people ages 20-79 who have type 1 or type 2 diabetes. It is calculated by adjusting to a standard population age-structure.

### Aggregation method:
Weighted average

### Statistical concept and methodology:
Methodology: The data used to estimate diabetes prevalence were gathered from various sources. Most of the data were extracted from peer-reviewed publications and national health surveys, including selected WHO STEPwise approach to surveillance (WHO STEPS) studies. Additionally, data from other official sources, such as registries and reports from health regulatory bodies, were utilized, provided there was sufficient information to assess their quality. Data sources with adequate methodological information on key areas of interest, such as the method of diagnosis and sample representativeness, were included. Given the significance of age as a major determinant for diabetes prevalence, only studies with at least three age-specific estimates were considered. After selecting the data sources, the reported age- and sex-specific data in each source were smoothed using a logistic regression model.

### Development relevance:
Diabetes, an important cause of ill health and a risk factor for other diseases in developed countries, is spreading rapidly in developing countries. Highest among the elderly, prevalence rates are rising among younger and productive populations in developing countries. Economic development has led to the spread of Western lifestyles and diet to developing countries, resulting in a substantial increase in diabetes. Without effective prevention and control programs, diabetes will likely continue to increase.

### Limitations and exceptions:
The limited availability of data on health status is a major constraint in assessing the health situation in developing countries. Surveillance data are lacking for many major public health concerns. Estimates of prevalence and incidence are available for some diseases but are often unreliable and incomplete. National health authorities differ widely in capacity and willingness to collect or report information.

### Source

#### International Diabetes Federation (Diabetes Atlas), via World Bank – World Development Indicators
Retrieved on: 2026-07-27  
Retrieved from: https://data.worldbank.org/indicator/SH.STA.DIAB.ZS  


    