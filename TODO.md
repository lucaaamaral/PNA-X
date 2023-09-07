# Activities to be done  <!-- omit in toc -->

- [1. Test:](#1-test)
  - [1.1. Parameter config:](#11-parameter-config)
    - [1.1.1. Hardcoded values removed and passed as arguments](#111-hardcoded-values-removed-and-passed-as-arguments)
    - [1.1.2. Calibration kit messsage ommission when none is provided from the PNA](#112-calibration-kit-messsage-ommission-when-none-is-provided-from-the-pna)
  - [1.2. Guided Calibration](#12-guided-calibration)
    - [1.2.1. input message without {i} value](#121-input-message-without-i-value)
  - [1.3. Save cal set](#13-save-cal-set)
    - [1.3.1. Verify if it saves or delete and saves to the PNA-x](#131-verify-if-it-saves-or-delete-and-saves-to-the-pna-x)
  - [1.4. ComPt graphics plot](#14-compt-graphics-plot)
  - [1.5. Atenuator offset](#15-atenuator-offset)
  - [1.6. ADS data export](#16-ads-data-export)
- [2. Develop:](#2-develop)
  - [2.1. Break parameter\_config functions in some more functions](#21-break-parameter_config-functions-in-some-more-functions)
  - [2.2. Update commands to newer versions of SCPI](#22-update-commands-to-newer-versions-of-scpi)
  - [2.3. Improve manner selecions are made](#23-improve-manner-selecions-are-made)
  - [2.4. instanciate global session to be able not to pass as argument](#24-instanciate-global-session-to-be-able-not-to-pass-as-argument)
  - [2.5. place graphic plot in a separated thread](#25-place-graphic-plot-in-a-separated-thread)



# 1. Test:
## 1.1. Parameter config:
### 1.1.1. Hardcoded values removed and passed as arguments
### 1.1.2. Calibration kit messsage ommission when none is provided from the PNA
## 1.2. Guided Calibration
### 1.2.1. input message without {i} value
## 1.3. Save cal set
### 1.3.1. Verify if it saves or delete and saves to the PNA-x
There must only be one entry at the PNA-x for the calibration set
## 1.4. ComPt graphics plot
## 1.5. Atenuator offset
## 1.6. ADS data export


# 2. Develop:
## 2.1. Break parameter_config functions in some more functions
## 2.2. Update commands to newer versions of SCPI
calculate marker -> malculate measure marker
## 2.3. Improve manner selecions are made
Using arrows or some kind of selector [Ultra low priority]
## 2.4. instanciate global session to be able not to pass as argument
## 2.5. place graphic plot in a separated thread
