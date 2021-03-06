#!/usr/bin/env python
# -- coding: utf-8 --
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from desktop.lib.exceptions_renderable import PopupException

from search.api import SolrApi
from search.conf import SOLR_URL
from search.models import Collection
from django.utils.translation import ugettext as _


LOG = logging.getLogger(__name__)


class SearchController(object):
  """
  Glue the models to the views.
  """
  def __init__(self, user):
    self.user = user

  def get_search_collections(self):
    # TODO perms
    return Collection.objects.filter(enabled=True)

  def delete_collection(self, collection_id):
    id = collection_id
    try:
      Collection.objects.get(id=collection_id).delete()
    except Exception, e:
      LOG.warn('Error deleting collection: %s' % e)
      id = -1

    return id

  def copy_collection(self, collection_id):
    id = -1

    try:
      copy = Collection.objects.get(id=collection_id)
      copy.label += _(' (Copy)')
      copy.id = copy.pk = None
      copy.save()

      facets = copy.facets
      facets.id = None
      facets.save()
      copy.facets = facets

      result = copy.result
      result.id = None
      result.save()
      copy.result = result


      sorting = copy.sorting
      sorting.id = None
      sorting.save()
      copy.sorting = sorting

      copy.save()

      id = copy.id
    except Exception, e:
      LOG.warn('Error copying collection: %s' % e)

  def is_collection(self, collection_name):
    solr_collections = SolrApi(SOLR_URL.get(), self.user).collections()
    return collection_name in solr_collections

  def is_core(self, core_name):
    solr_cores = SolrApi(SOLR_URL.get(), self.user).cores()
    return core_name in solr_cores

  def get_solr_collection(self):
    return SolrApi(SOLR_URL.get(), self.user).collections()

  def get_all_indexes(self):
    return self.get_solr_collection().keys() + SolrApi(SOLR_URL.get(), self.user).cores().keys()
