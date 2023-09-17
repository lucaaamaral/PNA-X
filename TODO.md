# Activities to be done  <!-- omit in toc -->

- [1. Test](#1-test)
  - [1.1. ADS data export](#11-ads-data-export)
  - [1.2. Test ```session.resource_manager.close()``` in PNA-X and implement in other files](#12-test-sessionresource_managerclose-in-pna-x-and-implement-in-other-files)
  - [1.3. Remove magic values in ComPt and SParamCal](#13-remove-magic-values-in-compt-and-sparamcal)
- [2. Develop](#2-develop)
  - [2.1. Break parameter\_config functions in some more functions](#21-break-parameter_config-functions-in-some-more-functions)
  - [2.2. Update commands to newer versions of SCPI](#22-update-commands-to-newer-versions-of-scpi)
  - [2.3. Improve manner selecions are made](#23-improve-manner-selecions-are-made)
  - [2.4. instanciate global session to be able not to pass as argument](#24-instanciate-global-session-to-be-able-not-to-pass-as-argument)
  - [2.5. place graphic plot in a separated thread](#25-place-graphic-plot-in-a-separated-thread)
  - [2.6. Pyvisa takes too long to finish](#26-pyvisa-takes-too-long-to-finish)
  - [2.7. Graphical interface](#27-graphical-interface)
    - [2.7.1. Code refactor to adapt to the screens](#271-code-refactor-to-adapt-to-the-screens)
    - [2.7.2. Using GTK+ library](#272-using-gtk-library)
    - [2.7.3. API with HTML server in a separated thread](#273-api-with-html-server-in-a-separated-thread)
      - [2.7.3.1. Function's API for interacting with HTML's javascript](#2731-functions-api-for-interacting-with-htmls-javascript)
  - [2.8. Document functions](#28-document-functions)
  - [2.9. Setup characterization](#29-setup-characterization)

## 1. Test

### 1.1. ADS data export

### 1.2. Test ```session.resource_manager.close()``` in PNA-X and implement in other files

### 1.3. Remove magic values in ComPt and SParamCal

## 2. Develop

### 2.1. Break parameter_config functions in some more functions

### 2.2. Update commands to newer versions of SCPI

calculate marker -> malculate measure marker

### 2.3. Improve manner selecions are made

Graphic interface now.

### 2.4. instanciate global session to be able not to pass as argument

### 2.5. place graphic plot in a separated thread

### 2.6. Pyvisa takes too long to finish

Use close() method for the ResourceManager in question.
Related to [this](#12-test-sessionresource_managerclose-in-pna-x-and-implement-in-other-files).

### 2.7. Graphical interface

Choose wether will be GTK+ or web interface.

#### 2.7.1. Code refactor to adapt to the screens

#### 2.7.2. Using GTK+ library

#### 2.7.3. API with HTML server in a separated thread

##### 2.7.3.1. Function's API for interacting with HTML's javascript

### 2.8. Document functions

### 2.9. Setup characterization

Document table attenuation.
