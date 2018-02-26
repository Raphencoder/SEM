# Changelog
All notable changes to SEM will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

## [SEM v3.1.0](https://github.com/YoannDupont/SEM/releases/tag/v3.1.0)
### Added
- new module: ```map_annotations```. Modifies annotations' types given a mapping
- new exporter: ```html_inline```. Inserts HTML span tags in the document
- new exporter: ```tei_reden```. Generates a [REDEN](https://github.com/cvbrandoe/REDEN) XML TEI file
- new master file ```NER-REDEN.xml```.
- new CSS file ```default-no_empty_spans.css```. No default highlight with black background and white font
- changelog file ```changelog.md```. Clearer than previous "latest changes". Better history too.
- resource file ```REDEN-NER-map```. The mapping between SEM and [REDEN](https://github.com/cvbrandoe/REDEN) annotations for NER
- random one-liner when the user types a module for which SEM ha no suggestions.
### Changed
- ```export``` module improved. Handle multiple data formats
    - some exporters where changed to handle documents without annotations
- ```tei``` exporter renamed ```tei_analec```
- setup:
    - handle the absence of tkinter by not installing GUI modules
    - only ovewrite SEM data folder if forced (TODO: use setuptools install object to add option)
- tagger module: better handle options and output formats
- segmentation module: handle raw HTML by checking MIME type
- document type: added MIME type metadata
- importers: added logging

## [SEM v3.0.0](https://github.com/YoannDupont/SEM/releases/tag/v3.0.0)
### Added
- SEM can now be installed.
    - run ```python setup.py install --user```
    - will compile Wapiti
    - will create a sem_data folder in current user
- another GUI created for annotating documents.
- new module: ```annotate```. Allows to call python taggers
    - python implementation of Wapiti labeling
    - lexica-based tagger
### Changed
- improved SEM architecture
- updated manual
- more tests
    - tests for features
    - tests for modules

## changes compared to other versions:
unrealeased: https://github.com/YoannDupont/SEM/compare/v3.1.0...HEAD
3.1.0: https://github.com/YoannDupont/SEM/compare/v3.0.0...v3.1.0