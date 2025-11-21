![navi parser](https://github.com/user-attachments/assets/7461c8ab-8f12-4dc3-ac64-e39273e24442)

 # :blue_heart: Na'vi Language Grammar Parser :blue_heart:

*Na'vi sentence analyzer using the dictionary API. The program automatically identifies parts of speech, grammatical characteristics, and creates a visualization of the POS-distribution.*

</div>

## :page_facing_up: Features

- **Linguistic accuracy**: based on [dict-navi.com](https://dict-navi.com) data 
- **API Integration:** Fetches word data from Navi dictionary API
- **Data Visualization**: Creates POS distribution pie charts
- **Modular Architecture**: Clean separation of concerns between API, visualization, and analysis
- **Comprehensive Logging**: Tracks all operations with method-level logging

## :open_file_folder: Installation

```bash
git clone https://github.com/your-username/navi-parser.git
cd navi-parser
pip install -r requirements.txt
```

## :computer: Basic Usage 
```python
from navi_analyzer import NaviAnalysisFacade

# Запуск анализа
facade = NaviAnalysisFacade("config.yaml")
results = facade.run_pipeline()
```

## Dependencies
- **requests**: Access to API
- **pandas**: Easy and accessible output format 
- **matplotlib**: Chart generation

<div align="center">
 
*P.S This project is made purely for educational and linguistic research purposes.*

</div> 
