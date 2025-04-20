# SakurAI - Super Smash Bros. Frame Data & Analysis

SakurAI is a comprehensive data collection and analysis toolkit for fighting games, initially focusing on Super Smash Bros. Ultimate. This project aims to help players learn frame data while developing data science skills and improving gameplay through data-driven insights.

## Project Goals

- **Collect and organize** comprehensive frame data for all fighting game characters
- **Visualize** complex frame data in intuitive and insightful ways
- **Analyze** matchups, move properties, and game mechanics
- **Improve** player decision-making through data-driven insights
- **Learn** data science skills through practical application

## Current Features

### Data Extraction

- **Character Data**: Comprehensive attributes for all 89 SSBU characters
- **Move Data**: Detailed frame data for all character moves
- **Hitbox Data**: Precise hitbox information including damage, angle, knockback
- **Throw Data**: Frame-perfect throw information

### Data Sources

SakurAI combines data from multiple sources to create the most comprehensive dataset:

- [Ultimate Hitboxes](https://github.com/RSN-Bran/ultimate-hitboxes) - Core move and hitbox data
- [SSBU-Calculator](https://github.com/rubendal/SSBU-Calculator) - Character attributes and calculations
- Additional data sources to be integrated

## Getting Started

### Prerequisites

- Python 3.8+
- Pandas
- Git

### Installation

1. Clone the repository:
```
git clone https://github.com/Gadget622/SakurAI.git
cd SakurAI
```

2. Clone the data source repositories:
```
git clone https://github.com/RSN-Bran/ultimate-hitboxes.git
git clone https://github.com/rubendal/SSBU-Calculator.git
```

3. Run the data extraction scripts:
```
python data_extractor_csv.py
python character_attributes_extractor_csv.py
python data_merger.py
```

## Data Structure

SakurAI organizes fighting game data into several CSV files:

- `characters.csv` - Core character attributes and properties
- `moves.csv` - Move properties including frame data
- `hitboxes.csv` - Detailed hitbox information
- `throws.csv` - Throw mechanics and properties

## Future Plans

### Game Support Expansion

- **Street Fighter 6**: Expand data collection to include SF6 frame data
- **Rivals of Aether 2**: Support for RoA2 upon release
- **Other Fighting Games**: Framework to add support for additional games

### Feature Development

- Interactive web application via GitHub Pages
- Advanced matchup analysis tools
- Frame data visualization dashboard
- Combo database and analyzer
- Machine learning for matchup predictions

### Data Science Applications

- Cluster analysis of character archetypes
- Predictive modeling for matchup advantages
- Interactive dashboards for game analysis
- Statistical analysis of game balance

## Contributing

Contributions are welcome! Whether you're interested in:

- Adding data for new games
- Improving data accuracy
- Developing visualization tools
- Creating analysis methodologies

Please feel free to open issues or pull requests.

## Acknowledgments

- [Ultimate Hitboxes](https://github.com/RSN-Bran/ultimate-hitboxes) for their extensive frame data
- [SSBU-Calculator](https://github.com/rubendal/SSBU-Calculator) for character attribute information
- The Smash Ultimate community for their dedication to game knowledge

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

*Note: SakurAI is not affiliated with Nintendo or any fighting game publisher. All game data is collected from public sources for educational purposes.*