from demo_api.dto import SessionData, UserAuthentication, UserDetailed
from demo_api.dto.user_update import UserUpdate
from demo_api.storage.exceptions import NotFoundError
from .fixtures import *


async def test_user_registration(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    resulting_user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )
    assert resulting_user.user_id and resulting_user.is_active


async def test_user_authentication(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    resulting_user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_repo.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    assert resulting_user.user_id == authenticated_user.user_id


async def test_user_authentication_for_missing_user(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    with pytest.raises(NotFoundError):
        await user_repo.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )


async def test_user_authentication_with_invalid_password(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    with pytest.raises(ValueError):
        await user_repo.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password + "12345678"
            ),
            hashing_settings
        )


async def test_user_session_auth(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_repo.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    user_from_session: UserDetailed = await user_repo.get_user_by_session(
        authenticated_user.session_id
    )

    assert authenticated_user.user_id == user_from_session.user_id


async def test_user_session_auth_via_not_existing_session(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_repo.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    with pytest.raises(NotFoundError):
        await user_repo.get_user_by_session(
            authenticated_user.session_id + "12345678"
        )


async def test_fetching_user_details(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    registered_user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    fetched_user: UserDetailed = await user_repo.get_user(
        registered_user.user_id
    )

    assert fetched_user.user_id == registered_user.user_id
    assert fetched_user.name == registered_user.name


async def test_user_session_termination(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_repo.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    user_from_session: UserDetailed = await user_repo.get_user_by_session(
        authenticated_user.session_id
    )

    assert authenticated_user.user_id == user_from_session.user_id

    assert await user_repo.terminate_session(
        authenticated_user
    )

    with pytest.raises(NotFoundError):
        await user_repo.get_user_by_session(
            authenticated_user.session_id
        )


async def test_user_terminating_all_sessions(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    sessions: list[SessionData] = []
    for _ in range(5):
        authenticated_user: SessionData = await user_repo.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )
        sessions.append(authenticated_user)

        assert (await user_repo.get_user_by_session(
            authenticated_user.session_id
        )).user_id == user.user_id

    assert await user_repo.terminate_all_sessions(
        user.user_id
    )

    for user_session in sessions:
        with pytest.raises(NotFoundError):
            await user_repo.get_user_by_session(
                user_session.session_id
            )


async def test_fetching_many_users(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    for i in range(10):
        user_credentials.email = f"{i}{user_credentials.email}"
        await user_repo.register_user(
            user_credentials,
            UserPermissions(),
            hashing_settings
        )

    assert len(await user_repo.list_users(limit=10)) == 10


async def test_terminating_user(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    authenticated_user: SessionData = await user_repo.login(
        UserAuthentication(
            email=user_credentials.email,
            password=user_credentials.password
        ),
        hashing_settings
    )

    user_from_session: UserDetailed = await user_repo.get_user_by_session(
        authenticated_user.session_id
    )

    assert authenticated_user.user_id == user_from_session.user_id

    assert await user_repo.terminate_user(authenticated_user.user_id)

    with pytest.raises(NotFoundError):
        await user_repo.get_user_by_session(
            authenticated_user.session_id
        )

    with pytest.raises(NotFoundError):
        await user_repo.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )

async def test_fetching_many_users_with_deactivated(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    for i in range(10):
        user_credentials.email = f"{i}{user_credentials.email}"
        await user_repo.register_user(
            user_credentials,
            UserPermissions(),
            hashing_settings
        )

    assert len(await user_repo.list_users(limit=10, include_deactivated=True)) == 10


async def test_user_changing_password(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )

    sessions: list[SessionData] = []
    for _ in range(5):
        authenticated_user: SessionData = await user_repo.login(
            UserAuthentication(
                email=user_credentials.email,
                password=user_credentials.password
            ),
            hashing_settings
        )
        sessions.append(authenticated_user)

        assert (await user_repo.get_user_by_session(
            authenticated_user.session_id
        )).user_id == user.user_id

    assert await user_repo.change_user_password(
        user.user_id, "TestPassword12345678", hashing_settings
    )

    for user_session in sessions:
        with pytest.raises(NotFoundError):
            await user_repo.get_user_by_session(
                user_session.session_id
            )


async def test_updating_user_data(
    user_repo: UsersRepositorySQLA,
    user_credentials: UserRegistration,
    hashing_settings: HashingSettings
):
    user: User = await user_repo.register_user(
        user_credentials,
        UserPermissions(),
        hashing_settings
    )
    update_details: UserUpdate = UserUpdate(
        user_id=user.user_id,
        email=f"example_for_testing_updates_{secrets.token_urlsafe(8)}@example.com",
        name="Hello",
        surname="World",
        third_name="Some text"
    )

    updated_details: UserDetailed = await user_repo.update_user_details(update_details)
    assert updated_details == await user_repo.get_user(user.user_id)
