![navi parser](https://github.com/user-attachments/assets/7461c8ab-8f12-4dc3-ac64-e39273e24442)

 # :blue_heart: Na'vi Language Grammar Parser :blue_heart:

*A Python-based library for grammatical analysis and morphological processing of the Na'vi language from James Cameron's Avatar universe*

</div>

## :page_facing_up: Features
- **Complete Part-of-Speech System**: Nouns, pronouns, verbs, adjectives, numbers, and particles
- **Morphological Processing**: Case declension, verb infixes, number marking
- **Syntax Processing**: Dependency trees, word order
- **Visualization**: Simple and clear presentation of results, report generation
- **Grammatical Accuracy**: Based on the official [Na'vi reference grammar](https://files.learnnavi.org/docs/horen-lenavi.pdf)
- **Object-Oriented Design**: Clean, extensible class hierarchy

## :open_file_folder: Installation

```bash
git clone https://github.com/your-username/navi-parser.git
cd navi-parser
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## Basic Usage 
```bash
from navi_parser import create_parser

# Create parser with default settings
parser = create_parser()

# Analyze a sentence
result = parser.analyze_sentence("Oel ngati kameie")
```

## Advanced Usage 
```bash
# Full analysis with all features
parser = create_parser(
    use_linguistic_analysis=True,  # Uses spaCy for enhanced analysis
    enable_visualization=True,     # Generates charts and graphs
    verbose=True                   # Detailed console output
)
```

## Single sentence parsing
```bash
from navi_parser import create_parser

# Initialize parser
parser = create_parser(
    use_linguistic_analysis=True,
    enable_visualization=True,
    verbose=True
)

# Analyze with automatic visualization
result = parser.analyze_sentence(
    "Oel ngati kameie ma tsmukan",
    save_plots=True
)
```
## Batch sentence parsing
```bash
# Analyze multiple sentences
sentences = [
    "Oel ngati kameie",
    "Kaltxì ma frapo", 
    "Nga za'u ftu po"
]

results = parser.analyze_multiple_sentences(
    sentences,
    create_dashboard=True,
    save_dashboard=True
)
```
<div align="center">
 
*P.S This project is made purely for educational and linguistic research purposes.*

</div> 
