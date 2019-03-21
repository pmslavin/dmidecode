    def t_DMIDECODE(t):
        r"dmidecode"
        return t

    def t_SMBIOS(t):
        r"SMBIOS"
        return t

    def t_PRESENT(t):
        r"present\.*"
        return t

    def t_MEMDEV_HEAD(t):
        r"Memory\sDevice"
        return t

    def t_ARR_HANDLE(t):
        r"Array\sHandle"
        return t

    def t_TOT_WIDTH(t):
        r"Total\sWidth"
        return t

    def t_DATA_WIDTH(t):
        r"Data\sWidth"
        return t

    def t_SIZE(t):
        r"Size"
        return t

    def t_FORM_FACTOR(t):
        r"Form\sFactor"
        return t

    def t_SET(t):
        r"Set"
        return t

    def t_LOCATOR(t):
        r"Locator"
        return t

    def t_BANK_LOCATOR(t):
        r"Bank\sLocator"
        return t

    def t_TYPE_DETAIL(t):


    def t_SERIAL(t):
        r"Serial\sNumber"
        return t

    def t_ASSET_TAG(t):
        r"Asset\sTag"
        return t

    def t_PART_NUM(t):
        r"Part\sNumber"
        return t

    def t_RANK(t):
        r"Rank"
        return t

    def t_CLOCK_SPEED(t):
        r"Configured\sClock\sSpeed"
        return t

