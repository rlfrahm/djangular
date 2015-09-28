from rest_framework import permissions

BAR_OWNERS = 'Bar Owner'
DRINKERS = 'Drinkers'

def is_in_group(user, group_name):
  return user.groups.filter(name=group_name).exists()

class HasGroupPermission(permissions.BasePermission):
  """
  Ensure user is in required groups.
  """
  def has_permission(self, request, view):
    # Get a mapping of methods -> required group.
    required_groups_mapping = getattr(view, 'required_groups', {})

    # Determine the required groups for this particular request method.
    required_groups = required_groups_mapping.get(request.method, [])

    # Return True if the user has all the required groups.
    return all([is_in_group(request.user, group_name) for group_name in required_groups])