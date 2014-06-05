# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.http import Http404

from nose.tools import eq_

from oneanddone.base.tests import TestCase
from oneanddone.tasks.forms import TaskForm
from oneanddone.tasks.models import TaskKeyword
from oneanddone.tasks.tests import TaskFactory, TaskKeywordFactory
from oneanddone.users.tests import UserFactory


class TaskFormTests(TestCase):

    def test_initial_contains_list_of_keywords_for_existing_task(self):
        """
        Initial should contain the list of keywords from the task instance.
        """
        task = TaskFactory.create()
        TaskKeywordFactory.create_batch(3, task=task)
        form = TaskForm(instance=task)
        eq_(form.initial['keywords'], 'test1, test2, test3')

    def test_initial_contains_empty_list_of_keywords_for_new_task(self):
        """
        Initial should contain an empty list of keywords for a new task.
        """
        task = TaskFactory.create()
        form = TaskForm(instance=task)
        eq_(form.initial['keywords'], '')

    def test_save_processes_keywords_correctly(self):
        """
        Saving the form should update the keywords correctly.
        - Removed keywords should be removed
        - New keywords should be added
        - Remaining keywords should remain
        """
        user = UserFactory.create()
        task = TaskFactory.create()
        TaskKeywordFactory.create_batch(3, task=task)
        data = {
            'keywords': 'test3, new_keyword',
            'team': task.team.id,
        }
        for field in ('name', 'short_description', 'execution_time', 'difficulty',
                      'repeatable', 'instructions', 'is_draft'):
            data[field] = getattr(task, field)
        form = TaskForm(instance=task, data=data)
        form.save(user)

        removed_keyword = TaskKeyword.objects.filter(task=task, name='test1')
        eq_(len(removed_keyword), 0)

        added_keyword = TaskKeyword.objects.filter(task=task, name='new_keyword')
        eq_(len(added_keyword), 1)

        kept_keyword = TaskKeyword.objects.filter(task=task, name='test3')
        eq_(len(kept_keyword), 1)

        # double-check on the keywords_list property
        eq_(task.keywords_list, 'test3, new_keyword')
