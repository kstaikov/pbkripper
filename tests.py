import unittest
from pbk_ripper import get_output_filename

class ParsingTestCase(unittest.TestCase):
    def test_get_output_filename(self):
        filenames = (
            ('hwnrqhls_worg219-ep_m1080-16x9-720p-720p-3000k.m3u8', ('02', '19')),
            ('hwnrqhls_worg2519-ep_m1080-16x9-720p-720p-3000k.m3u8', ('25', '19')),
            ('b5575724_worg809_episode_m1080-16x9-hls-2500k.m3u8', ('08', '09')),
            ('arur903_episodea_m1080-4x3-hls-2500k.m3u8', ('09', '03')),
            ('xbq7bqnk_wilks501-ep_mezz-16x9-hls-2500k.m3u8', ('05', '01')),
            ('893d5285_wddg_ep102_15mbs_1080p-16x9-hls-2500k.m3u8', ('01', '02')),
            ('893d5285_wddg_ep1402_15mbs_1080p-16x9-hls-2500k.m3u8', ('14', '02')),
            ('vpeuouyy_cuge901a-ep_m1080-16x9-720p-720p-3000k.m3u8', ('09', '01')),
            ('vpeuouyy_cuge9201a-ep_m1080-16x9-720p-720p-3000k.m3u8', ('92', '01')),
            ('ll_web108_master_m1080-16x9-hls-2500k.m3u8', ('01', '08')),
            ('ll_web2508_master_m1080-16x9-hls-2500k.m3u8', ('25', '08')),
            ('b40e4792_ot_e119_national_version-16x9-hls-2500k.m3u8', ('01', '19')),
            ('b40e4792_ot_e1219_national_version-16x9-hls-2500k.m3u8', ('12', '19')),
            ('plum1427_ff2_clem_encoded_h264-16x9-hls-2500k.m3u8', ('14', '27')),
            ('plum127_ff2_clem_encoded_h264-16x9-hls-2500k.m3u8', ('01', '27')),
            ('4hv7eiqk_sesa4714_m1080-16x9-720p-720p-3000k.m3u8', ('47', '14')),
            ('cb73363c_thof1301-ep_m1080-16x9-hls-2500k.m3u8', ('13', '01')),
            ('7f5a82b4_thof1009_fullepisode_m1080-16x9-hls-2500k.m3u8', ('10', '09')),

            # These are extra tricky real cases. Don't know what to do with them, they have
            # No obvious season and episode number
            #'d5f0e167_cybr_monster_minutes_ep4-16x9-hls-2500k.m3u8',
            #'5681b05f_noac_outlimb_m1080-16x9-hls-2500k.m3u8',
            #'ce84752d_ruffunboxing_fullmix-16x9-hls-2500k.m3u8',
            #'bd779650_ruff_qa1v4-16x9-hls-2500k.m3u8',
        )

        for filename in filenames:
            output = get_output_filename(filename[0], 'title', 'title')
            expected_output = f'title - S{filename[1][0]}E{filename[1][1]} - title.ts'

            self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()
