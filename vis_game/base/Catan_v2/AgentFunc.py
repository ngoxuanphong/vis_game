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
    # Knight: Có là được dùng
    if p_state[191] == 1:
        list_action[55] = 1

    # Roadbuilding: Còn đường và còn vị trí xây đường
    if p_state[192] == 1 and p_state[79] == -1 and check_firstPoint(p_state):
        list_action[56] = 1

    # Yearofplenty: Ngân hàng có tài nguyên
    if p_state[193] == 1 and (p_state[48:53] == 1).any():
        list_action[57] = 1

    # Monopoly: Có là được dùng
    if p_state[194] == 1:
        list_action[58] = 1

@njit
def getValidActions(p_state: np.ndarray):
    phase = p_state[186]
    list_action = np.full(AMOUNT_ACTION, 0)

    if phase == 11:  # Yêu cầu tài nguyên khi trade với người
        # Nếu đã có ít nhất 1 tài nguyên, thì phải có action dừng
        if (p_state[201:206] > 0).any():
            list_action[104] = 1

        # Các action thêm tài nguyên: các loại tài nguyên mà không có trong phần đưa ra
        # list_action[59:64] = p_state[196:201] == 0
        for i in range(5):
            if p_state[196+i] == 0:
                list_action[59+i] = 1

        return list_action

    if phase == 6:  # Chọn các mô đun giữa turn
        check_useDev(p_state, list_action)

        if (p_state[54:59] >= ROAD_PRICE).all():
            # Mua đường (86)
            if p_state[79] == -1 and check_firstPoint(p_state):
                list_action[86] = 1

            # Mua nhà (87)
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

        # Mua thành phố (88)
        if (p_state[54:59] >= CITY_PRICE).all() and p_state[80] != -1 and p_state[88] == -1:
            list_action[88] = 1

        # Mua thẻ dev (89)
        if (p_state[54:59] >= DEV_PRICE).all() and p_state[53] == 1:
            list_action[89] = 1

        if (p_state[54:59] > 0).any():
            # Trade với người (90)
            if p_state[195] > 0 and (p_state[np.array([96, 125, 154])] > 0).any():
                list_action[90] = 1

            # Trade với bank (91)
            if (p_state[54:59] >= p_state[91:96]).any():
                temp = np.where(p_state[54:59] >= p_state[91:96])[0]
                for res in temp:
                    for res_1 in range(5):
                        if res_1 != res and p_state[48+res_1] == 1:
                            list_action[91] = 1
                            break

                    if list_action[91] == 1:
                        break

        # Kết thúc lượt (92)
        list_action[92] = 1

        return list_action

    if phase == 10:  # Đưa ra tài nguyên khi trade với người
        # Nếu đã có ít nhất 1 tài nguyên, thì phải có action dừng
        if (p_state[196:201] > 0).any():
            list_action[103] = 1

        # Các action thêm tài nguyên: các tài nguyên mà bản thân có
        # list_action[95:100] = p_state[54:59] > p_state[196:201]
        for i in range(5):
            if p_state[54+i] > p_state[196+i]:
                list_action[95+i] = 1

        # Nếu số loại tài nguyên bỏ vào là 4 thì không cho bỏ loại thứ 5 vào
        if np.count_nonzero(p_state[196:201] > 0) == 4:
            list_action[95+np.argmin(p_state[196:201])] = 0

        return list_action

    if phase == 3:  # Trả tài nguyên do bị chia bài
        # list_action[95:100] = p_state[54:59] > 0
        for i in range(5):
            if p_state[54+i] > 0:
                list_action[95+i] = 1

        return list_action

    if phase == 12:  # Người chơi phụ phản hồi trade
        # Action từ chối: 93, Action: đồng ý: 94
        list_action[93:95] = 1

        # Vào pha này thì chắc chắn người chơi phụ phải có thể trade
        # if (p_state[54:59] >= p_state[196:201]).all():
        #     list_action[94] = 1

        return list_action

    if phase == 15:  # Chọn tài nguyên muốn nhận từ ngân hàng
        # Chọn những tài nguyên mà ngân hàng có, khác tài nguyên đưa ra
        list_action[59:64] = p_state[48:53]
        list_action[59+np.argmax(p_state[196:201])] = 0

        return list_action

    if phase == 14:  # Chọn tài nguyên khi trade với ngân hàng
        # Chọn những tài nguyên mà khi chọn, ngân hàng còn ít nhất 1 loại tài nguyên khác
        # temp = np.where(p_state[54:59] >= p_state[91:96])[0]
        # for res in temp:
        for res in range(5):
            if p_state[54+res] >= p_state[91+res]:
                for res_1 in range(5):
                    if res_1 != res and p_state[48+res_1] == 1:
                        list_action[95+res] = 1
                        break

        return list_action

    if phase == 1:  # Chọn các điểm đầu mút của đường
        if p_state[187] == -1:  # Chọn điểm thứ nhất
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

    if phase == 4:  # Di chuyển Robber
        list_action[64:83] = 1
        list_action[int(64+p_state[19])] = 0

        return list_action

    if phase == 13:  # Người chơi chính duyệt trade
        # Action bỏ qua
        list_action[105] = 1

        # Chọn người để trade
        # Vào pha này thì chắc chắn có ít nhất một người đồng ý trade
        list_action[100:103] = p_state[206:209]

        return list_action

    if phase == 5:  # Chọn người để cướp tài nguyên
        robber_pos = int(p_state[19])
        for i in range(3):
            s_ = 96 + 29*i
            if p_state[s_] > 0:  # Chỉ xét khi có tài nguyên
                temp = p_state[s_+18:s_+27].astype(np.int32)
                for point in temp:
                    if point != -1 and point in TILE_POINT[robber_pos]:
                        list_action[83+i] = 1
                        break

        return list_action

    if phase == 2:  # Đổ xx hoặc dùng thẻ dev
        # Đổ xx
        list_action[54] = 1

        check_useDev(p_state, list_action)

        return list_action

    if phase == 0:  # Chọn điểm đặt nhà đầu game
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

    if phase == 8:  # Chọn các điểm mua nhà
        p_point, all_stm_and_city = get_p_point_n_all_stm_city(p_state)
        list_point = np.where(p_point == 1)[0]
        for point in list_point:
            list_road = POINT_ROAD[point][POINT_ROAD[point] != -1]
            nearest_points = ROAD_POINT[list_road].flatten()
            if (all_stm_and_city[nearest_points] == 0).all():
                list_action[point] = 1

        return list_action

    if phase == 7:  # Chọn tài nguyên khi dùng thẻ dev
        if p_state[189] == 2:  # Đang dùng yearofplenty
            list_action[59:64] = p_state[48:53]
        elif p_state[189] == 3:  # Đang dùng monopoly
            list_action[59:64] = 1

        return list_action

    if phase == 9:  # Chọn các điểm mua thành phố
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
