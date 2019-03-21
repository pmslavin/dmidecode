"""
dmidecode memory report parser

BNF for `dmidecode -t memory` output:

    decode          ::= preamble arrayspec? bankarray
    preamble        ::= decoder_version SMBIOS_TEXT smbios_version

    arrayspec       ::= handlehead arrayspec_body
    arrayspec_body  ::= phys_head arrayspec_lines
    arrayspec_lines ::= arrayspec_lines arrayspec_line
                     |  arrayspec_line

    bankarray       ::= bankarray bankspec
                     |  bankspec

    bankspec        ::= bank_head banklines
    banklines       ::= banklines bankline
                     |  bankline

    decoder_version ::= '#' 'dmidecode' VERSION
    SMBIOS_TEXT     ::= 'Getting SMBIOS data from sysfs.'
    smbios_version  ::= 'SMBIOS' VERSION 'present.'
"""
import ply.lex
import ply.yacc


def parse_dmi(src):
    base_tokens      = ('NEWLINE', 'INT', 'DESC', 'ADDRHEX', 'VERSION', 'SMBIOS_TEXT', 'DMIDECODE', 'SMBIOS',
                        'PRESENT', 'HANDLE', 'DMI_TYPE', 'BYTECOUNT', 'FF_TYPE')

    physarray_tokens = ('PHYS_HEAD', 'LOCATION', 'USE', 'EC_TYPE', 'MAX_CAP', 'ERRINFO_HANDLE', 'NUM_DEVICES',
                        'MEM_SIZE')

    memdevice_tokens = ('MEMDEV_HEAD', 'ARR_HANDLE', 'TOT_WIDTH', 'DATA_WIDTH', 'SIZE', 'FORM_FACTOR', 'SET',
                       'LOCATOR', 'BANK_LOCATOR', 'TYPE', 'TYPE_DETAIL', 'SPEED', 'MANUFACTURER', 'SERIAL',
                       'ASSET_TAG', 'PART_NUM', 'RANK', 'CLOCK_SPEED')

    memctrl_tokens   = ('MEMCTRL_HEAD', 'ERR_DETECT_MT', 'ECC_CAPS', 'SUPP_ILEAVE', 'CURR_ILEAVE', 'MAX_MOD_SIZE',
                        'MAX_TOT_MEM_SIZE', 'SUPP_SPEED', 'SUPP_TYPE', 'MOD_VOLTS', 'ASSOC_SLOTS', 'ECC_ENABLED' )

    memmod_tokens    = ('MEMMOD_HEAD', 'SOCK_DSGN', 'BANK_CONN', 'CUR_SPEED', 'INSTALL_SIZE', 'ENABLE_SIZE', 'ERR_STATUS' )


    tokens = base_tokens + physarray_tokens + memdevice_tokens + memctrl_tokens + memmod_tokens

    literals = (':', '#', ',')
    t_ignore = ' \t'

    base_idents = { 'Getting SMBIOS data from sysfs.' : 'SMBIOS_TEXT'
                  }

    physarray_idents = { 'Physical Memory Array' : 'PHYS_HEAD',
                         'Location' : 'LOCATION',
                         'Use' : 'USE',
                         'Error Correction Type' : 'EC_TYPE',
                         'Maximum Capacity' : 'MAX_CAP',
                         'Error Information Handle' : 'ERRINFO_HANDLE',
                         'Number Of Devices' : 'NUM_DEVICES',
                         'Memory Size' : 'MEM_SIZE'
                       }

    memdevice_idents = { 'Memory Device' : 'MEMDEV_HEAD',
                         'Array Handle'  : 'ARR_HANDLE',
                         'Total Width' : 'TOT_WIDTH',
                         'Data Width' : 'DATA_WIDTH',
                         'Size' : 'SIZE',
                         'Form Factor' : 'FORM_FACTOR',
                         'Set' : 'SET',
                         'Locator' : 'LOCATOR',
                         'Bank Locator' : 'BANK_LOCATOR',
                         'Type' : 'TYPE',
                         'Type Detail' : 'TYPE_DETAIL',
                         'Speed' : 'SPEED',
                         'Manufacturer' : 'MANUFACTURER',
                         'Serial Number' : 'SERIAL',
                         'Asset Tag' : 'ASSET_TAG',
                         'Part Number' : 'PART_NUM',
                         'Rank' : 'RANK',
                         'Configured Clock Speed' : 'CLOCK_SPEED'
                       }

    memctrl_idents  =  { 'Memory Controller Information' : 'MEMCTRL_HEAD',
                         'Error Detecting Method' : 'ERR_DETECT_MT',
                         'Error Correcting Capabilities' : 'ECC_CAPS',
                         'Supported Interleave' : 'SUPP_ILEAVE',
                         'Current Interleave' : 'CURR_ILEAVE',
                         'Maximum Memory Module Size' : 'MAX_MOD_SIZE',
                         'Maximum Total Memory Size' : 'MAX_TOT_MEM_SIZE',
                         'Supported Speeds' : 'SUPP_SPEED',
                         'Supported Memory Types' : 'SUPP_TYPE',
                         'Memory Module Voltage' : 'MOD_VOLTS',
                         'Associated Memory Slots' : 'ASSOC_SLOTS',
                         'Enabled Error Correcting Capabilities' : 'ECC_ENABLED'
                       }

    memmod_idents   =  { 'Memory Module Information' : 'MEMMOD_HEAD',
                         'Socket Designation' : 'SOCK_DSGN',
                         'Bank Connections' : 'BANK_CONN',
                         'Current Speed' : 'CUR_SPEED',
                         'Installed Size' : 'INSTALL_SIZE',
                         'Enabled Size' : 'ENABLE_SIZE',
                         'Error Status' : 'ERR_STATUS'
                       }

    idents = {}
    idents.update(base_idents)
    idents.update(physarray_idents)
    idents.update(memdevice_idents)
    idents.update(memctrl_idents)
    idents.update(memmod_idents)


# Predefined symbols
    symbols = {}

# Tokens
    def t_error(t):
        raise SyntaxError("Unknown symbol '{0}': line {1}".format(t.value.split()[0], t.lexer.lineno+1))
        print "Skipping", repr(t.value[0])
        t.lexer.skip(1)

    def t_NEWLINE(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_DMIDECODE(t):
        r"dmidecode"
        return t

    def t_SMBIOS(t):
        r"SMBIOS"
        return t

    def t_PRESENT(t):
        r"present\.*"
        return t

    def t_HANDLE(t):
        r"Handle"
        return t

    def t_MEM_SIZE(t):
        r"\d+\s[GMK]B"
        size, unit = t.value.split()
        t.value = (int(size), unit)
        return t

    def t_FF_TYPE(t):
        r"\bDIMM(?![0-9 _])|\bSDRAM\b"
        return t

    def t_DMI_TYPE(t):
        r"DMI\stype\s[0-9]+"
        digits = t.value.split()[-1]
        t.value = int(digits)
        return t

    def t_BYTECOUNT(t):
        r"[0-9]+\sbytes"
        digits = t.value.split()[0]
        t.value = int(digits)
        return t

    def t_ADDRHEX(t):
        r"0[xX][0-9A-F]+"
        return t

    def t_VERSION(t):
        r"[0-9]+\.[0-9]+"
        major, minor = t.value.split('.')
        t.value = (major, minor)
        return t

    def t_DESC(t):
        r"[\]\[\)\(\w\-\./_ ]+"
        t.type = idents.get(t.value, 'DESC')
        return t



# Productions
    def p_error(p):
        print("Parse error: {0}".format(p))
        raise ValueError("Syntax error, line {0}: {1}".format(p.lineno, p.type))
#        parser.errok()
#        token = parser.token()
#        token.value = "BIOS_BLANK_OMITS_{0}".format(token.type)
#        return token


    def p_decode(p):
        r"""decode    : preamble bodyspecs"""
        p[0] = [p[1], p[2]]

    def p_preamble(p):
        r"""preamble  : decoder_version SMBIOS_TEXT smbios_version
                      | decoder_version smbios_version"""
        if len(p) == 4:
            p[0] = [p[1], p[3]]
        elif len(p) == 3:
            p[0] = [p[1], p[2]]

    def p_decoder_version(p):
        r"""decoder_version   : '#' DMIDECODE VERSION"""
        p[0] = p[3]

    def p_smbios_version(p):
        r"""smbios_version    : SMBIOS VERSION PRESENT"""
        p[0] = p[2]

    def p_bodyspecs(p):
        r"""bodyspecs       : bodyspecs bodyspec
                            | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []

    def p_bodyspec(p):
        r"""bodyspec        : physarray
                            | memdevice
                            | memctrl
                            | memmod"""
        p[0] = p[1]

    def p_memmod(p):
        r"""memmod          : handlehead memmod_body"""
        p[0] = (p[1], p[2])

    def p_memmod_body(p):
        r"""memmod_body     : MEMMOD_HEAD memmod_lines"""
        p[0] = p[2]

    def p_memmod_lines(p):
        r"""memmod_lines    : memmod_lines memmod_line
                            | """

        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []

    def p_memmod_line(p):
        r"""memmod_line     : SOCK_DSGN ':' desctext
                            | BANK_CONN ':' desctext
                            | CUR_SPEED ':' desctext
                            | TYPE ':' desctext
                            | INSTALL_SIZE ':' MEM_SIZE desctext
                            | INSTALL_SIZE ':' desctext
                            | ENABLE_SIZE ':' MEM_SIZE desctext
                            | ENABLE_SIZE ':' desctext
                            | ERR_STATUS ':' desctext"""
        p[0] = (p[1], p[3])

    def p_memctrl(p):
        r"""memctrl         : handlehead memctrl_body"""
        p[0] = (p[1], p[2])

    def p_memctrl_body(p):
        r"""memctrl_body    : MEMCTRL_HEAD memctrl_lines"""
        p[0] = p[2]

    def p_memctrl_lines(p):
        r"""memctrl_lines   : memctrl_lines memctrl_line
                            | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []

    def p_memctrl_line(p):
        r"""memctrl_line    : ERR_DETECT_MT ':' desctext
                            | ECC_CAPS ':' desctext
                            | SUPP_ILEAVE ':' desctext
                            | CURR_ILEAVE ':' desctext
                            | MAX_MOD_SIZE ':' MEM_SIZE
                            | MAX_TOT_MEM_SIZE ':' MEM_SIZE
                            | SUPP_SPEED ':' desctext
                            | SUPP_TYPE ':' ff_type_list
                            | MOD_VOLTS ':' VERSION desctext
                            | ASSOC_SLOTS ':' desctext slotlist
                            | ECC_ENABLED ':' desctext"""
        if len(p) == 4:
            p[0] = (p[1], p[3])
        elif len(p) == 5:
            p[0] = (p[1], p[3], p[4])

    def p_ff_type_list(p):
        r"""ff_type_list    : ff_type_list FF_TYPE
                            | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []

    def p_slotlist(p):
        r"""slotlist        : slotlist ADDRHEX
                            | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []

    def p_memdevice(p):
        r"""memdevice       : handlehead memdevice_body"""
        p[0] = (p[1], p[2])

    def p_memdevice_body(p):
        r"""memdevice_body  : MEMDEV_HEAD memdevice_lines"""
        p[0] = (p[1], p[2])

    def p_memdevice_lines(p):
        r"""memdevice_lines : memdevice_lines memdevice_line
                            | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []

    def p_memdevice_line(p):
        r"""memdevice_line  : ERRINFO_HANDLE ':' desctext
                            | ARR_HANDLE ':' ADDRHEX
                            | TOT_WIDTH ':' desctext
                            | DATA_WIDTH ':' desctext
                            | SIZE ':' MEM_SIZE
                            | SIZE ':' desctext
                            | FORM_FACTOR ':' FF_TYPE
                            | SET ':' desctext
                            | LOCATOR ':' desctext
                            | BANK_LOCATOR ':' desctext
                            | TYPE ':' desctext
                            | TYPE_DETAIL ':' desctext
                            | SPEED ':' desctext
                            | MANUFACTURER ':' desctext
                            | SERIAL ':' desctext
                            | ASSET_TAG ':' desctext
                            | PART_NUM ':' desctext
                            | RANK ':' desctext
                            | CLOCK_SPEED ':' desctext"""
        p[0] = (p[1], p[3])

    def p_physarray(p):
        r"physarray         : handlehead physarray_body"
        p[0] = (p[1], p[2])

    def p_handlehead(p):
        r"handlehead        : HANDLE ADDRHEX ',' DMI_TYPE ',' BYTECOUNT"
        p[0] = [p[2], p[4], p[6]]

    def p_physarray_body(p):
        r"physarray_body    : PHYS_HEAD physarray_lines"
        p[0] = (p[1], [p[2]])

    def p_physarray_lines(p):
        r"""physarray_lines   : physarray_lines physarray_line
                              | """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        elif len(p) == 1:
            p[0] = []


    def p_physarray_line(p):
        r"""physarray_line   : LOCATION ':' desctext
                             | USE ':' desctext
                             | EC_TYPE ':' desctext
                             | MAX_CAP ':' MEM_SIZE
                             | ERRINFO_HANDLE ':' desctext
                             | NUM_DEVICES ':' desctext"""

        p[0] = (p[1], p[3])


    def p_desctext(p):
        r"""desctext        : DESC
                            | """
        if len(p) == 2:
            p[0] = p[1]
        else:
            pass


    lexer  = ply.lex.lex(debug=1)
    parser = ply.yacc.yacc()

    try:
        return parser.parse(src, lexer=lexer, debug=1)
    except ValueError as err:
        print("[ValueError] {0}".format(err))
        return []


if __name__ == "__main__":
    import sys
    from pprint import pprint

    src = """# dmidecode 3.0
Getting SMBIOS data from sysfs.
SMBIOS 2.7 present.

Handle 0x000D, DMI type 16, 23 bytes
Physical Memory Array
    Location: System Board Or Motherboard
    Use: System Memory
    Error Correction Type: None
    Maximum Capacity: 32 GB
    Number Of Devices: 4
    Error Information Handle: Not Provided

Handle 0x000E, DMI type 17, 34 bytes
Memory Device
    Array Handle: 0x000D
    Error Information Handle: Not Provided
    Total Width: Unknown
    Data Width: Unknown
    Size: No Module Installed
    Form Factor: DIMM
    Set: None
    Type: Unknown
    Type Detail: None
    Speed: Unknown
    Manufacturer: Empty
    Serial Number: 0025E8E6
    Part Number: Empty
    Rank: Unknown
    Configured Clock Speed: Unknown
    Asset Tag: 9876543210
    Locator: DIMM4
    Bank Locator: BANK 3"""

    src = sys.stdin.read()

    ret = parse_dmi(src)
    pprint(ret)
