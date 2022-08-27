# ==========================
# CONFLUENCE Server version
# ==========================

ADMIN_USRNAME="username"
echo -n "Enter Pass:"
read -s ADMIN_USRPWD

CONFLUENCE_BASE_URL="<your_confluence_server_url>"
SPACE_KEYS=('PRJ1' 'PRJ2')
API_METHOD=getSpacePermissionSets

for SPACE_KEY in "${SPACE_KEYS[@]}"
do
    curl --user $ADMIN_USRNAME:$ADMIN_USRPWD \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -X POST \
        -d '{ "jsonrpc" : "2.0", "method" : "'${API_METHOD}'", "params" : ["'${SPACE_KEY}'"], "id": 7 }' \
        ${CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic 2>/dev/null | jq -r '.result' > "$SPACE_KEY".txt
done


# ACTION=$1

# do_removeUserPermissionsInSpace(){
#     curl --user "$ADMIN_USRNAME:$ADMIN_USRPWD" \
#         -H "Content-Type: application/json" \
#         -H "Accept: application/json" \
#         -X POST \
#         -d '{ "jsonrpc" : "2.0", "method" : "'${API_METHOD}'", "params" : ["'${2}'", "'${1}'", "'${3}'"], "id": 7 }' \
#         ${CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic
# }

# if [[ $ACTION = "bkp" ]]; then
#     API_METHOD=getSpacePermissionSets
#     # It generates a file per space

#     for SPACE_KEY in "${SPACE_KEYS[@]}"
#     do
#         curl --user $ADMIN_USRNAME:$ADMIN_USRPWD \
#             -H "Content-Type: application/json" \
#             -H "Accept: application/json" \
#             -X POST \
#             -d '{ "jsonrpc" : "2.0", "method" : "'${API_METHOD}'", "params" : ["'${SPACE_KEY}'"], "id": 7 }' \
#             ${CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic 2>/dev/null | jq -r '.result[]' > "$SPACE_KEY".txt
#     done
# elif [[ $ACTION = "del" ]]; then
#     API_METHOD=removePermissionFromSpace
#     # It reads the bkp file generated in the previous action

#     for SPACE_KEY in "${SPACE_KEYS[@]}"
#     do
#         jq -c '.result[].spacePermissions[] | { type: .type, userName: .userName } | select( (.userName != null) and .type != "VIEWSPACE")' "$SPACE_KEY".txt | while read i; do
#             username=$(echo "$i" | jq -r .userName)
#             perm=$(echo "$i" | jq -r .type)
#             do_removeUserPermissionsInSpace "$username" "$perm" "$SPACE_KEY"
#         done
#     done
# else
#     echo "Invalid ACTION '$ACTION' "
# fi


# CONFLUENCE_BASE_URL=https://COMPANY.atlassian.net/

# # curl -u ${ADMIN_USRNAME}:${ADMIN_TOKEN} -X GET "${CONFLUENCE_BASE_URL}/wiki/rest/api/content?title=0000_For_Test%20(86433)&spaceKey=EPAR&expand=history" | python -mjson.tool
# # exit

# echo -n "Enter Pass:"
# # read -s ADMIN_USRPWD

# SPACE_KEYS=('PRJ1')
# API_METHOD=getSpacePermissionSets

# for SPACE_KEY in "${SPACE_KEYS[@]}"
# do
#     # curl --user $ADMIN_USRNAME:$ADMIN_TOKEN \
#     #     -H "Content-Type: application/json" \
#     #     -H "Accept: application/json" \
#     #     -X POST \
#     #     -d '{ "jsonrpc" : "2.0", "method" : "'${API_METHOD}'", "params" : ["'${SPACE_KEY}'"], "id": 7 }' \
#     #     ${CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic
#     #     # ${CONFLUENCE_BASE_URL}/rpc/json-rpc/confluenceservice-v2?os_authType=basic 2>/dev/null | jq -r '.result[]' > "$SPACE_KEY".txt
#     curl --request GET \
#     --url "${CONFLUENCE_BASE_URL}/wiki/rest/api/space" \
#     --user $ADMIN_USRNAME:$ADMIN_TOKEN \
#     --header 'Accept: application/json'
# done