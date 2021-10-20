import json
from fastapi import FastAPI, Depends, status
from typing import Optional
from fastapi.exceptions import HTTPException

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


with open("menu.json", "r") as read_file:

    data = json.load(read_file)

app = FastAPI()

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "asdf": {
        "username": "asdf",
        "full_name": "Alice Sasa Demi Flora",
        "email": "alice@example.com",
        "hashed_password": "fakehashedasdf",
        "disabled": False,
    },
}

def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# -----------*********-----------
@app.get('/menu/{item_id}')
async def read_menu(item_id: int, current_user: User = Depends(get_current_active_user)):
    for menu_item in data['menu']:

        if menu_item['id'] == item_id:
            return menu_item
    
    raise HTTPException(

status_code=404, detail=f'Item not found'

)




@app.put('/menu/{item_id}')
async def update_menu(item_id: int, name:str, current_user: User = Depends(get_current_active_user)):
    for menu_item in data['menu']:

        if menu_item['id'] == item_id:
            menu_item['name'] = name
            read_file.close()
            with open('menu.json', 'w') as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()

            return{'message':'Data berhasil diupdate'}

    raise HTTPException(

status_code=404, detail=f'Item not found'

)

@app.delete('/menu/{item_id}')
async def delete_menu(item_id: int,current_user: User = Depends(get_current_active_user)):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()
            with open('menu.json', 'w') as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()

            return{'message':'Data berhasil dihapus'}

    raise HTTPException(

status_code=404, detail=f'Item not found'

)

@app.post('/menu')
async def post_menu(name:str, current_user: User = Depends(get_current_active_user)):
    id=1
    if(len(data['menu'])>0):
        id = data['menu'][len(data['menu'])-1]['id']+1
    new_data={'id':id, 'name':name}
    data['menu'].append(dict(new_data))

    read_file.close()
    with open('menu.json', 'w') as write_file:
        json.dump(data, write_file, indent=4)
    write_file.close()
    return(new_data)
 
    raise HTTPException(
        status_code=500, detail=f'Could not post'
    )