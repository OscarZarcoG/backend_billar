def organize_tags(generator, request, public, result):
    paths = result.get('paths', {})

    def normalize(p: str) -> str:
        if p.startswith('/api/'):
            return p[4:]
        return p

    for path, operations in paths.items():
        np = normalize(path)
        for method, op in list(operations.items()):
            if method.lower() not in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                continue
            new_tag = None
            if np.startswith('/auth/social/'):
                new_tag = 'Social Authentication'
            elif np.startswith('/auth/users/'):
                if '/by-role' in np or np.endswith('/by-role/'):
                    new_tag = 'Roles'
                elif '/change-role' in np:
                    new_tag = 'Roles'
                else:
                    new_tag = 'Users'
            elif np.startswith('/auth/'):
                new_tag = 'Authentication'
            if new_tag:
                op['tags'] = [new_tag]

    result['tags'] = [
        {'name': 'Authentication', 'description': 'Login, registration and logout'},
        {'name': 'Users', 'description': 'User management'},
        {'name': 'Roles', 'description': 'Role management'},
        {'name': 'Social Authentication', 'description': 'Social login (Google, GitHub)'},
    ]
    return result
