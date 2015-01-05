'''streamcorpus-pipeline transform for generating line-based "zone" assignments

'''


from streamcorpus import OffsetType, Offset


class zoner(object):

    def process_item(self, si, context=None):

        tags = run_zoner(si.body.clean_visible)
        for line_number, zone_number in tags:
            off = Offset(
                type=OffsetType.LINES,
                first=tag,
                length=1,
                value=zone_number,
            )
            #si.body.zones
