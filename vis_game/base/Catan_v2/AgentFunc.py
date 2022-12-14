from vis_game.base.Catan_v2.relation import *
from numba import njit

@njit
def get_p_point_n_all_road(p_state: np.ndarray):
    p_point = np.zeros(54)
    all_road = np.zeros(72)

    temp = p_state[65:80].astype(np.int32)
    for road in temp:
        if road == -1:
            break
        else:
            all_road[road] = 1
            p_point[ROAD_POINT[road]] = 1

    for j in range(3):
        s_ = 96 + 29*j

        temp = p_state[s_+3:s_+18].astype(np.int32)
        for road in temp:
            if road == -1:
                break
            else:
                all_road[road] = 1

        temp = p_state[s_+18:s_+23].astype(np.int32)
        for i in temp:
            if i == -1:
                break
            else:
                p_point[i] = 0

        temp = p_state[s_+23:s_+27].astype(np.int32)
        for i in temp:
            if i == -1:
                break
            else:
                p_point[i] = 0

    return p_point, all_road

@njit
def get_p_point_n_all_stm_city(p_state: np.ndarray):
    p_point = np.zeros(54)
    all_stm_and_city = np.zeros(54)

    temp = p_state[65:80].astype(np.int32)
    for i in temp:
        if i == -1:
            break
        else:
            p_point[ROAD_POINT[i]] = 1

    temp = p_state[80:85].astype(np.int32)
    for i in temp:
        if i == -1:
            break
        else:
            all_stm_and_city[i] = 1
            p_point[i] = 0

    temp = p_state[85:89].astype(np.int32)
    for i in temp:
        if i == -1:
            break
        else:
            all_stm_and_city[i] = 1
            p_point[i] = 0

    for j in range(3):
        s_ = 96 + 29*j

        temp = p_state[s_+18:s_+23].astype(np.int32)
        for i in temp:
            if i == -1:
                break
            else:
                all_stm_and_city[i] = 1
                p_point[i] = 0

        temp = p_state[s_+23:s_+27].astype(np.int32)
        for i in temp:
            if i == -1:
                break
            else:
                all_stm_and_city[i] = 1
                p_point[i] = 0

    return p_point, all_stm_and_city

@njit
def check_firstPoint(p_state: np.ndarray):
    p_point, all_road = get_p_point_n_all_road(p_state)
    list_point = np.where(p_point == 1)[0]
    for point in list_point:
        for road in POINT_ROAD[point]:
            if road != -1 and all_road[road] == 0:
                return True

    return False

@njit
def check_useDev(p_state: np.ndarray, list_action: np.ndarray):
    # Knight: C?? l?? ???????c d??ng
    if p_state[191] == 1:
        list_action[55] = 1

    # Roadbuilding: C??n ???????ng v?? c??n v??? tr?? x??y ???????ng
    if p_state[192] == 1 and p_state[79] == -1 and check_firstPoint(p_state):
        list_action[56] = 1

    # Yearofplenty: Ng??n h??ng c?? t??i nguy??n
    if p_state[193] == 1 and (p_state[48:53] == 1).any():
        list_action[57] = 1

    # Monopoly: C?? l?? ???????c d??ng
    if p_state[194] == 1:
        list_action[58] = 1

@njit
def getValidActions(p_state: np.ndarray):
    phase = p_state[186]
    list_action = np.full(AMOUNT_ACTION, 0)

    if phase == 11:  # Y??u c???u t??i nguy??n khi trade v???i ng?????i
        # N???u ???? c?? ??t nh???t 1 t??i nguy??n, th?? ph???i c?? action d???ng
        if (p_state[201:206] > 0).any():
            list_action[104] = 1

        # C??c action th??m t??i nguy??n: c??c lo???i t??i nguy??n m?? kh??ng c?? trong ph???n ????a ra
        # list_action[59:64] = p_state[196:201] == 0
        for i in range(5):
            if p_state[196+i] == 0:
                list_action[59+i] = 1

        return list_action

    if phase == 6:  # Ch???n c??c m?? ??un gi???a turn
        check_useDev(p_state, list_action)

        if (p_state[54:59] >= ROAD_PRICE).all():
            # Mua ???????ng (86)
            if p_state[79] == -1 and check_firstPoint(p_state):
                list_action[86] = 1

            # Mua nh?? (87)
            if (p_state[54:59] >= SETTLEMENT_PRICE).all() and p_state[84] == -1:
                p_point, all_stm_and_city = get_p_point_n_all_stm_city(p_state)
                list_point = np.where(p_point == 1)[0]
                for point in list_point:
                    # list_road = POINT_ROAD[point][POINT_ROAD[point] != -1]
                    # nearest_points = ROAD_POINT[list_road].flatten()
                    # if (all_stm_and_city[nearest_points] == 0).all():
                    #     list_action[87] = 1
                    #     break
                    check = True
                    for road in POINT_ROAD[point]:
                        if road != -1:
                            for neares_point in ROAD_POINT[road]:
                                if all_stm_and_city[neares_point] == 1:
                                    check = False
                                    break

                            if not check:
                                break

                    if check:
                        list_action[87] = 1
                        break

        # Mua th??nh ph??? (88)
        if (p_state[54:59] >= CITY_PRICE).all() and p_state[80] != -1 and p_state[88] == -1:
            list_action[88] = 1

        # Mua th??? dev (89)
        if (p_state[54:59] >= DEV_PRICE).all() and p_state[53] == 1:
            list_action[89] = 1

        if (p_state[54:59] > 0).any():
            # Trade v???i ng?????i (90)
            if p_state[195] > 0 and (p_state[np.array([96, 125, 154])] > 0).any():
                list_action[90] = 1

            # Trade v???i bank (91)
            if (p_state[54:59] >= p_state[91:96]).any():
                temp = np.where(p_state[54:59] >= p_state[91:96])[0]
                for res in temp:
                    for res_1 in range(5):
                        if res_1 != res and p_state[48+res_1] == 1:
                            list_action[91] = 1
                            break

                    if list_action[91] == 1:
                        break

        # K???t th??c l?????t (92)
        list_action[92] = 1

        return list_action

    if phase == 10:  # ????a ra t??i nguy??n khi trade v???i ng?????i
        # N???u ???? c?? ??t nh???t 1 t??i nguy??n, th?? ph???i c?? action d???ng
        if (p_state[196:201] > 0).any():
            list_action[103] = 1

        # C??c action th??m t??i nguy??n: c??c t??i nguy??n m?? b???n th??n c??
        # list_action[95:100] = p_state[54:59] > p_state[196:201]
        for i in range(5):
            if p_state[54+i] > p_state[196+i]:
                list_action[95+i] = 1

        # N???u s??? lo???i t??i nguy??n b??? v??o l?? 4 th?? kh??ng cho b??? lo???i th??? 5 v??o
        if np.count_nonzero(p_state[196:201] > 0) == 4:
            list_action[95+np.argmin(p_state[196:201])] = 0

        return list_action

    if phase == 3:  # Tr??? t??i nguy??n do b??? chia b??i
        # list_action[95:100] = p_state[54:59] > 0
        for i in range(5):
            if p_state[54+i] > 0:
                list_action[95+i] = 1

        return list_action

    if phase == 12:  # Ng?????i ch??i ph??? ph???n h???i trade
        # Action t??? ch???i: 93, Action: ?????ng ??: 94
        list_action[93:95] = 1

        # V??o pha n??y th?? ch???c ch???n ng?????i ch??i ph??? ph???i c?? th??? trade
        # if (p_state[54:59] >= p_state[196:201]).all():
        #     list_action[94] = 1

        return list_action

    if phase == 15:  # Ch???n t??i nguy??n mu???n nh???n t??? ng??n h??ng
        # Ch???n nh???ng t??i nguy??n m?? ng??n h??ng c??, kh??c t??i nguy??n ????a ra
        list_action[59:64] = p_state[48:53]
        list_action[59+np.argmax(p_state[196:201])] = 0

        return list_action

    if phase == 14:  # Ch???n t??i nguy??n khi trade v???i ng??n h??ng
        # Ch???n nh???ng t??i nguy??n m?? khi ch???n, ng??n h??ng c??n ??t nh???t 1 lo???i t??i nguy??n kh??c
        # temp = np.where(p_state[54:59] >= p_state[91:96])[0]
        # for res in temp:
        for res in range(5):
            if p_state[54+res] >= p_state[91+res]:
                for res_1 in range(5):
                    if res_1 != res and p_state[48+res_1] == 1:
                        list_action[95+res] = 1
                        break

        return list_action

    if phase == 1:  # Ch???n c??c ??i???m ?????u m??t c???a ???????ng
        if p_state[187] == -1:  # Ch???n ??i???m th??? nh???t
            p_point, all_road = get_p_point_n_all_road(p_state)
            list_point = np.where(p_point == 1)[0]
            for point in list_point:
                for road in POINT_ROAD[point]:
                    if road != -1 and all_road[road] == 0:
                        list_action[point] = 1
                        break

            return list_action

        all_road = np.zeros(72)

        temp = p_state[65:80].astype(np.int32)
        for i in temp:
            if i == -1:
                break
            else:
                all_road[i] = 1

        for j in range(3):
            s_ = 96 + 29*j

            temp = p_state[s_+3:s_+18].astype(np.int32)
            for i in temp:
                if i == -1:
                    break
                else:
                    all_road[i] = 1

        first_point = int(p_state[187])
        for road in POINT_ROAD[first_point]:
            if road != -1 and all_road[road] == 0:
                list_action[ROAD_POINT[road]] = 1

        list_action[first_point] = 0

        return list_action

    if phase == 4:  # Di chuy???n Robber
        list_action[64:83] = 1
        list_action[int(64+p_state[19])] = 0

        return list_action

    if phase == 13:  # Ng?????i ch??i ch??nh duy???t trade
        # Action b??? qua
        list_action[105] = 1

        # Ch???n ng?????i ????? trade
        # V??o pha n??y th?? ch???c ch???n c?? ??t nh???t m???t ng?????i ?????ng ?? trade
        list_action[100:103] = p_state[206:209]

        return list_action

    if phase == 5:  # Ch???n ng?????i ????? c?????p t??i nguy??n
        robber_pos = int(p_state[19])
        for i in range(3):
            s_ = 96 + 29*i
            if p_state[s_] > 0:  # Ch??? x??t khi c?? t??i nguy??n
                temp = p_state[s_+18:s_+27].astype(np.int32)
                for point in temp:
                    if point != -1 and point in TILE_POINT[robber_pos]:
                        list_action[83+i] = 1
                        break

        return list_action

    if phase == 2:  # ????? xx ho???c d??ng th??? dev
        # ????? xx
        list_action[54] = 1

        check_useDev(p_state, list_action)

        return list_action

    if phase == 0:  # Ch???n ??i???m ?????t nh?? ?????u game
        list_action[0:54] = 1

        temp = p_state[np.array(
            [80, 81, 114, 115, 143, 144, 172, 173])].astype(np.int32)
        for stm in temp:
            if stm != -1:
                list_action[stm] = 0
                for point in POINT_POINT[stm]:
                    if point != -1:
                        list_action[point] = 0

        return list_action

    if phase == 8:  # Ch???n c??c ??i???m mua nh??
        p_point, all_stm_and_city = get_p_point_n_all_stm_city(p_state)
        list_point = np.where(p_point == 1)[0]
        for point in list_point:
            list_road = POINT_ROAD[point][POINT_ROAD[point] != -1]
            nearest_points = ROAD_POINT[list_road].flatten()
            if (all_stm_and_city[nearest_points] == 0).all():
                list_action[point] = 1

        return list_action

    if phase == 7:  # Ch???n t??i nguy??n khi d??ng th??? dev
        if p_state[189] == 2:  # ??ang d??ng yearofplenty
            list_action[59:64] = p_state[48:53]
        elif p_state[189] == 3:  # ??ang d??ng monopoly
            list_action[59:64] = 1

        return list_action

    if phase == 9:  # Ch???n c??c ??i???m mua th??nh ph???
        temp = p_state[80:85].astype(np.int32)
        for p_stm in temp:
            if p_stm == -1:
                break
            else:
                list_action[p_stm] = 1

        return list_action

    return list_action


@njit
def getStateSize():
    return LEN_P_STATE


@njit
def getActionSize():
    return AMOUNT_ACTION


@njit
def getAgentSize():
    return 4
