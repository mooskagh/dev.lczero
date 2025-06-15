# Visual Style Guide

* The website is done in Microtik Webfix-like style, i.e. almost industrial, win95-like.
* The main feature is density of information.
* Most of style is done through overriding the default style for elements, rather than relying on styles.
* The variables (colors, section sizes, element sizes, fonts) should be at the top of CSS with --vars.
* The CSS should be well maintainable.
* There should be no JS unless explicitly asked. No JS for styling, and no AJAX calls (old-school POST/GET requests instead).
* All CSS should be in separate .css file, no styles in HTML templates.
* No unused CSS classes in HTML templates.

## Layout

* Fonts:
  * For almost everything: "verdana, Helvetica, Arial, sans-serif;"
  * Size: 11px
  * For headers: bold
  * Text color everywhere: #000000
* Narrow top bar is for logo and login/logout button, and in future some buttons like "Help" or "Settings"
  * background color is #ddd
  * Height: 15px
* Left side menu is for main navigation, two levels (sections and items)
  * Width: 130px
  * Background color is #bbb
  * Items:
    * Look like buttons
      * Padding: 5px 10px
      * When non-selected, bg color is #ddd, shadow "1px 1px 2px rgba(255, 255, 255, 0.8) inset, 0 5px 10px -5px rgba(255, 255, 255, 0.7) inset;"
      * When selected, bg color is #aaa, and button is "pressed"
      * Are 100% for top level, and 3px left-right margins for level 2, with background color #c1c1c1
      * Every menu item may have a small 16×16px icon on the left side. If there is no icon, keep space for it.
* The rest of the page is for content
  * Background color is #f0f0f0

### Tables

* White background, with 1px solid #888 border
* #dedede for headers. With bold text. And looking a bit like a button.
* Tables that are narrow (everything fits one line), should not stretch to full width.

### Minibuttons and checkboxes:

* Checkboxes that look like buttons with a single letter inside are called "minibuttons"
* Also buttons and links may be minibuttons
{
    display: inline;
    border-top-color: #d0d0d0;
    border-left-color: #d0d0d0;
    border-bottom-color: #606060;
    border-right-color: #606060;
    border-style: solid;
    border-width: 1px;
    padding: 0px 4px 0px 3px;
    margin: 0 0 0 2px;
    font-size: 10px;
    text-decoration: none;
    color: #000000;
    background: #e0e0e0;
    cursor: inherit;
}

### Buttons

* Also look like win95 buttons

## Implementation Plan

### Phase 1: Base CSS Framework

1. **Create base CSS structure**

   * Set up CSS variables for colors, fonts, and dimensions
   * Create reset/normalize styles
   * Define base element overrides (body, h1-h6, p, etc.)

2. **Implement core layout components**

   * Top navigation bar (#ddd background, 15px height)
   * Left sidebar menu (#bbb background, 130px width)
   * Main content area (#f0f0f0 background)

### Phase 2: Navigation Components

1. **Top bar implementation**

   * Logo placement
   * Login/logout button styling
   * Future-proof for additional buttons (Help, Settings)

2. **Sidebar menu system**

   * Two-level navigation structure
   * Button-like menu items with proper hover/selected states
   * Icon spacing (16×16px) for all menu items
   * Proper indentation for second-level items

### Phase 3: Content Components

1. **Table styling**

   * White background with #888 borders
   * Header styling (#dedede background, bold text)
   * Auto-width for narrow tables
   * Responsive behavior

2. **Form elements**

   * Minibuttons implementation
   * Standard button styling (Win95-like)
   * Checkbox and input field styling
   * Form layout and spacing

### Phase 4: Typography and Spacing

1. **Font system**

   * Verdana-based font stack
   * 11px base font size
   * Header font weights and sizes
   * Text color consistency (#000000)

2. **Spacing and layout refinements**

   * Consistent padding and margins
   * Content density optimization
   * Visual hierarchy establishment

### Phase 5: Integration and Testing

1. **Template integration**

   * Apply styles to existing Django templates
   * Remove any inline styles
   * Clean up unused CSS classes

2. **Cross-browser testing**

   * Ensure Win95-like appearance across browsers
   * Test responsive behavior
   * Validate CSS maintainability

### Phase 6: Documentation and Maintenance

1. **Style guide documentation**

   * CSS variable reference
   * Component usage examples
   * Maintenance guidelines

2. **Code review and optimization**

   * Remove unused CSS
   * Optimize for performance
   * Ensure maintainability standards

### Technical Considerations

* All CSS in separate .css files (no inline styles)
* No JavaScript for styling
* CSS variables for easy theme maintenance
* Industrial/Win95 aesthetic prioritized
* Information density over modern spacing
* Backward compatibility with older browsers
