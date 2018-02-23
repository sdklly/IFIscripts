import sys
import os
import subprocess
from lxml import etree
import ififuncs

def get_metadata(xpath_path, root, pbcore_namespace):
    value = root.xpath(
        xpath_path,
        namespaces={'ns':pbcore_namespace}
    )

    if value == []:
        value =  'n/a'
    else:
        value = value[0].text 
    return value


def make_csv(csv_filename):
    ififuncs.create_csv('bla.csv', [
        'Reference Number',
        'Donor',
        'Edited By',
        'Date Created',
        'Date Last Modified',
        'Film Or Tape',
        'Date Of Donation',
        'Accession Number',
        'Habitat',
        'Type Of Deposit',
        'Depositor Reference',
        'Master Viewing',
        'Language Version',
        'Condition Rating',
        'Companion Elements',
        'EditedNew',
        'FIO',
        'CollectionTitle',
        'Created By',
        'instantiationIdentif',
        'instantiationDate',
        'instantiationDimensi',
        'instantiationPhysica',
        'instantiationDigital',
        'instantiationStandar',
        'instantiationLocatio',
        'instantMediaty',
        'instantGenerations',
        'instantFileSize',
        'instantTimeStart',
        'instantDataRate',
        'instantColors',
        'instantLanguage',
        'instantAltMo',
        'essenceDataRate_vid',
        'essenceTrackEncodvid',
        'essenceFrameRate',
        'essenceTrackSampling',
        'essenceBitDepth_vid',
        'essenceFrameSize',
        'essenceAspectRatio',
        'essenceTrackEncod_au',
        'essenceDataRate_au',
        'essenceBitDepth_au',
        'instantiationDuratio',
        'instantiationChanCon',
        'PixelAspectRatio',
        'FrameCount',
        'ColorSpace',
        'ChromaSubsampling',
        'ScanType',
        'Interlacement',
        'Compression_Mode',
        'colour_primaries',
        'transfer_characteris',
        'matrix_coefficients'
    ])

def main():
    source = sys.argv[1]
    metadata = subprocess.check_output(['mediainfo', '--Output=PBCore2', source])
    root = etree.fromstring(metadata)
    pbcore_namespace = root.xpath('namespace-uri(.)')
    ScanType =  get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='ScanType']",
        root,pbcore_namespace
    )
    matrix_coefficients =  get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='matrix_coefficients']",
        root, pbcore_namespace
    )
    transfer_characteris =  get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='transfer_characteristics']",
        root, pbcore_namespace
    )
    colour_primaries =  get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='color_primaries']",
        root, pbcore_namespace
    )
    FrameCount = get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='FrameCount']",
        root, pbcore_namespace
    )
    ColorSpace = get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='ColorSpace']",
        root, pbcore_namespace
    )
    ChromaSubsampling =  get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='ChromaSubsampling']",
        root, pbcore_namespace
    )
    instantMediaty = get_metadata(
        "//ns:instantiationMediaType",
        root, pbcore_namespace
    )
    essenceFrameSize = get_metadata(
        "//ns:essenceTrackFrameSize",
        root, pbcore_namespace
    )
    essenceAspectRatio =  get_metadata(
        "//ns:essenceTrackAspectRatio",
        root, pbcore_namespace
    )
    PixelAspectRatio =  get_metadata(
        "//ns:essenceTrackAnnotation[@annotationType='PixelAspectRatio']",
        root, pbcore_namespace
    )
    instantiationDigital =  get_metadata(
        "//ns:instantiationAnnotation[@annotationType='Format_Commercial_IfAny']",
        root, pbcore_namespace
    )
    instantiationStandar =  get_metadata(
        "//ns:instantiationAnnotation[@annotationType='Format']",
        root, pbcore_namespace
    )
    essenceFrameRate =  get_metadata(
        "//ns:essenceTrackFrameRate",
        root, pbcore_namespace
    )
    essenceTrackSampling =  get_metadata(
        "//ns:essenceTrackSamplingRate",
        root, pbcore_namespace
    )
    Interlacement =  get_metadata(
        "//ns:instantiationAnnotation[@annotationType='Interlacement']",
        root, pbcore_namespace
    )
    Compression_Mode =  get_metadata(
        "//ns:instantiationAnnotation[@annotationType='Compression_Mode']",
        root, pbcore_namespace
    )
    ms = 0
    for i in os.listdir(os.path.dirname(source)):
        if i.endswith('mov'):
            ms += ififuncs.get_milliseconds(os.path.join(os.path.dirname(source), i))
    tc = ififuncs.convert_millis(ms)
    instantiationDuratio =  ififuncs.convert_timecode(25, tc)
    Reference_Number = ''
    Donor = ''
    Edited_By = ''
    Date_Created = ''
    Date_Last_Modified  = ''
    Film_Or_Tape = 'Digital File'
    Date_Of_Donation = ''
    Accession_Number = ''
    Habitat = ''
    Type_Of_Deposit = ''
    Depositor_Reference = ''
    Master_Viewing = 'Preservation Master'
    Language_Version = ''
    Condition_Rating = ''
    Companion_Elements = ''
    EditedNew = ''
    FIO = 'In'
    CollectionTitle = ''
    Created_By = ''
    instantiationIdentif = ''
    instantiationDate = ''
    instantiationDimensi = ''
    instantiationPhysica =  'n/a'
    instantiationLocatio =  ''
    instantGenerations =  ''
    instantFileSize =  ''
    instantTimeStart =  ''
    instantDataRate =  ''
    instantColors =  ''
    instantLanguage =  ''
    instantAltMo =  'n/a'
    essenceDataRate_vid =  ''
    essenceTrackEncodvid =  ''
    essenceBitDepth_vid =  ififuncs.get_mediainfo(
        'duration', '--inform=Video;%BitDepth%', source
    )
    essenceTrackEncod_au =  ''
    essenceDataRate_au =  ''
    essenceBitDepth_au = ififuncs.get_mediainfo(
        'duration', '--inform=Audio;%BitDepth%', source
    )
    
    instantiationChanCon =  ''

    ififuncs.append_csv('bla.csv', [
        Reference_Number,
        Donor,
        Edited_By,
        Date_Created,
        Date_Last_Modified,
        Film_Or_Tape,
        Date_Of_Donation,
        Accession_Number,
        Habitat,
        Type_Of_Deposit,
        Depositor_Reference,
        Master_Viewing,
        Language_Version,
        Condition_Rating,
        Companion_Elements,
        EditedNew,
        FIO,
        CollectionTitle,
        Created_By,
        instantiationIdentif,
        instantiationDate,
        instantiationDimensi,
        instantiationPhysica,
        instantiationDigital,
        instantiationStandar,
        instantiationLocatio,
        instantMediaty,
        instantGenerations,
        instantFileSize,
        instantTimeStart,
        instantDataRate,
        instantColors,
        instantLanguage,
        instantAltMo,
        essenceDataRate_vid,
        essenceTrackEncodvid,
        essenceFrameRate,
        essenceTrackSampling,
        essenceBitDepth_vid,
        essenceFrameSize,
        essenceAspectRatio,
        essenceTrackEncod_au,
        essenceDataRate_au,
        essenceBitDepth_au,
        instantiationDuratio,
        instantiationChanCon,
        PixelAspectRatio,
        FrameCount,
        ColorSpace,
        ChromaSubsampling,
        ScanType,
        Interlacement,
        Compression_Mode,
        colour_primaries,
        transfer_characteris,
        matrix_coefficients])
if __name__ == '__main__':
    main()
