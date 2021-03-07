# -*- coding: utf-8 -*-
# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import re
import pytz
from frappe.model.document import Document
from frappe import _
from datetime import datetime
from six import string_types
from pyyoutube import Api

class Video(Document):
	def validate(self):
		if self.provider == "YouTube" and is_tracking_enabled():
			self.set_video_id()
			self.set_youtube_statistics()

	def set_video_id(self):
		if self.url and not self.get("youtube_video_id"):
			self.youtube_video_id = get_id_from_url(self.url)

	def set_youtube_statistics(self):
		api_key = frappe.db.get_single_value("Video Settings", "api_key")
		api = Api(api_key=api_key)

		try:
			video = api.get_video_by_id(video_id=self.youtube_video_id)
			video_stats = video.items[0].to_dict().get('statistics')

			self.like_count = video_stats.get('likeCount')
			self.view_count = video_stats.get('viewCount')
			self.dislike_count = video_stats.get('dislikeCount')
			self.comment_count = video_stats.get('commentCount')

		except Exception:
			title = "Failed to Update YouTube Statistics for Video: {0}".format(self.name)
			frappe.log_error(title + "\n\n" +  frappe.get_traceback(), title=title)

def is_tracking_enabled():
	return frappe.db.get_single_value("Video Settings", "enable_youtube_tracking")


def get_frequency(value):
	# Return numeric value from frequency field, return 1 as fallback default value: 1 hour
	if value != "Daily":
		return frappe.utils.cint(value[:2].strip())
	elif value:
		return 24
	return 1


def update_youtube_data():
	# Called every 30 minutes via hooks
	enable_youtube_tracking, frequency = frappe.db.get_value("Video Settings", "Video Settings", ["enable_youtube_tracking", "frequency"])

	if not enable_youtube_tracking:
		return

	frequency = get_frequency(frequency)
	time = datetime.now()
	timezone = pytz.timezone(frappe.utils.get_time_zone())
	site_time = time.astimezone(timezone)

	if frequency == 30:
		batch_update_youtube_data()
	elif site_time.hour % frequency == 0 and site_time.minute < 15:
		# make sure it runs within the first 15 mins of the hour
		batch_update_youtube_data()


def get_formatted_ids(video_list):
	# format ids to comma separated string for bulk request
	ids = []
	for video in video_list:
		ids.append(video.youtube_video_id)

	return ','.join(ids)


@frappe.whitelist()
def get_id_from_url(url):
	"""
		Returns video id from url
		:param youtube url: String URL
	"""
	if not isinstance(url, string_types):
		frappe.throw(_("URL can only be a string"), title=_("Invalid URL"))

	pattern = re.compile(r'[a-z\:\//\.]+(youtube|youtu)\.(com|be)/(watch\?v=|embed/|.+\?v=)?([^"&?\s]{11})?')
	id = pattern.match(url)
	return id.groups()[-1]


@frappe.whitelist()
def batch_update_youtube_data():
	def get_youtube_statistics(video_ids):
		api_key = frappe.db.get_single_value("Video Settings", "api_key")
		api = Api(api_key=api_key)
		try:
			video = api.get_video_by_id(video_id=video_ids)
			video_stats = video.items
			return video_stats
		except Exception:
			title = "Failed to Update YouTube Statistics"
			frappe.log_error(title + "\n\n" +  frappe.get_traceback(), title=title)

	def prepare_and_set_data(video_list):
		video_ids = get_formatted_ids(video_list)
		stats = get_youtube_statistics(video_ids)
		set_youtube_data(stats)

	def set_youtube_data(entries):
		for entry in entries:
			video_stats = entry.to_dict().get('statistics')
			video_id = entry.to_dict().get('id')
			stats = {
				'like_count' : video_stats.get('likeCount'),
				'view_count' : video_stats.get('viewCount'),
				'dislike_count' : video_stats.get('dislikeCount'),
				'comment_count' : video_stats.get('commentCount'),
				'video_id': video_id
			}

			frappe.db.sql("""
				UPDATE `tabVideo`
				SET
					like_count  = %(like_count)s,
					view_count = %(view_count)s,
					dislike_count = %(dislike_count)s,
					comment_count = %(comment_count)s
				WHERE youtube_video_id = %(video_id)s""", stats)

	video_list = frappe.get_all("Video", fields=["youtube_video_id"])
	if len(video_list) > 50:
		# Update in batches of 50
		start, end = 0, 50
		while start < len(video_list):
			batch = video_list[start:end]
			prepare_and_set_data(batch)
			start += 50
			end += 50
	else:
		prepare_and_set_data(video_list)
