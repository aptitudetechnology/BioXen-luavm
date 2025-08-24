Update the interactive-bioxen-lua.py file to use external package dictionaries from the pkgdict folder. 

TASK: Replace the inline BIOXEN_PACKAGES and BIOXEN_PROFILES dictionaries with imports from external files.

CHANGES NEEDED:
1. Remove the existing BIOXEN_PACKAGES dictionary (around lines 65-75) that contains:
  - bio-utils, sequence-parser, phylo-tree, blast-parser, genome-tools, protein-fold

2. Remove the existing BIOXEN_PROFILES dictionary (around lines 80-95) that contains:
  - bioxen-minimal, bioxen-standard, bioxen-full

3. Add these imports near the top of the file with other imports:
  from pkgdict.bioxen_packages import ALL_PACKAGES, BIOXEN_PACKAGES
  from pkgdict.bioxen_profiles import ALL_PROFILES, BIOXEN_PROFILES, PROFILE_CATEGORIES

4. Update any references to use the imported dictionaries instead of the inline ones

5. The pkgdict folder structure is:
  pkgdict/
  ├── __init__.py
  ├── bioxen_packages.py  
  └── bioxen_profiles.py

GOAL: Clean up the 874-line main file by moving package definitions to external dictionary files, making gabby-lua and lua-radio available in the package management system.

PRESERVE: All existing functionality - this is just moving data definitions to external files, not changing behavior.