const size = {
  xs: '600px',
  sm: '960px',
  md: '1264px',
  lg: '1904px',
};

const int_size = {
  xs: 600,
  sm: 960,
  md: 1264,
  lg: 1904,
};

const checkers = {
  xsOnly: () => {
    return window.innerWidth <= int_size.xs;
  },
  smAndDown: () => {
    return window.innerWidth <= int_size.sm;
  },
  smAndUp: () => {
    return window.innerWidth > int_size.xs;
  },
  mdAndDown: () => {
    return window.innerWidth <= int_size.md;
  },
  mdAndUp: () => {
    return window.innerWidth >= int_size.md;
  },
  lgAndUp: () => {
    return window.innerWidth >= int_size.lg;
  },
  getFlexWidth (col) {
    if (col >= 1 && col <= 12) {
      return `${(col / 12) * 100}%`;
    } else if (col === 0) {
      return '0%';
    } else {
      // Handle invalid column numbers, perhaps return 100% or throw an error
      return '100%';
    }
  }
};

const breakpoint = {
  size: size,
  devices_max: {
    xs: `max-width: ${size.xs}`,
    sm: `max-width: ${size.sm}`,
    md: `max-width: ${size.md}`,
    lg: `max-width: ${size.lg}`,
  },
  devices_min: {
    xs: `min-width: ${size.xs}`,
    sm: `min-width: ${size.sm}`,
    md: `min-width: ${size.md}`,
    lg: `min-width: ${size.lg}`,
  },
  checkers: checkers,
}

export default breakpoint;